#!/usr/bin/env python3
"""
Comprehensive Claude Code Notification Handler

Handles all Claude Code notification types with proper interactivity:
- Task duration tracking (like CCNotify)
- Click-to-open in configurable editor (Zed, VS Code, Cursor, etc.)
- Different sounds/urgency levels per notification type
- Session tracking with SQLite

Sources:
- https://code.claude.com/docs/en/hooks
- https://github.com/dazuiba/CCNotify (task tracking inspiration)
- https://github.com/hta218/claude-code-notifier (simplicity inspiration)
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Configuration from environment
NOTIFICATION_SOUND = os.getenv("NOTIFICATION_SOUND", "Glass")
EDITOR_COMMAND = os.getenv("NOTIFICATION_EDITOR", "zed")  # zed, code, cursor, etc.


class ClaudeNotifier:
    def __init__(self):
        """Initialize with database and logging"""
        self.base_dir = Path.home() / ".claude" / "notifier"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_dir / "sessions.db"
        self.log_path = self.base_dir / "notifier.log"

        self.setup_logging()
        self.init_database()

    def setup_logging(self):
        """Setup logging with daily rotation"""
        handler = TimedRotatingFileHandler(
            self.log_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def init_database(self):
        """Create tables for session tracking"""
        with sqlite3.connect(self.db_path) as conn:
            # Track prompts/tasks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    prompt TEXT,
                    cwd TEXT,
                    seq INTEGER,
                    completed_at DATETIME,
                    duration_seconds INTEGER
                )
            """)

            # Auto-increment seq per session
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS auto_seq
                AFTER INSERT ON tasks
                FOR EACH ROW
                BEGIN
                    UPDATE tasks
                    SET seq = (
                        SELECT COALESCE(MAX(seq), 0) + 1
                        FROM tasks
                        WHERE session_id = NEW.session_id
                    )
                    WHERE id = NEW.id;
                END
            """)

            conn.commit()

    # ========================================================================
    # Hook Handlers
    # ========================================================================

    def handle_user_prompt_submit(self, data):
        """UserPromptSubmit: Record task start"""
        session_id = data.get("session_id")
        prompt = data.get("prompt", "")
        cwd = data.get("cwd", "")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks (session_id, prompt, cwd) VALUES (?, ?, ?)",
                (session_id, prompt, cwd)
            )
            conn.commit()

        logging.info(f"Task started: session={session_id}")

    def handle_stop(self, data):
        """Stop: Task completed, show duration"""
        session_id = data.get("session_id")
        cwd = data.get("cwd", "")

        with sqlite3.connect(self.db_path) as conn:
            # Find latest incomplete task
            cursor = conn.execute(
                """
                SELECT id, created_at, seq
                FROM tasks
                WHERE session_id = ? AND completed_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session_id,)
            )

            row = cursor.fetchone()
            if row:
                task_id, created_at, seq = row

                # Update completion
                conn.execute(
                    """
                    UPDATE tasks
                    SET completed_at = CURRENT_TIMESTAMP,
                        duration_seconds = (
                            CAST((julianday(CURRENT_TIMESTAMP) - julianday(?)) * 86400 AS INTEGER)
                        )
                    WHERE id = ?
                    """,
                    (created_at, task_id)
                )
                conn.commit()

                # Get duration
                cursor = conn.execute(
                    "SELECT duration_seconds FROM tasks WHERE id = ?",
                    (task_id,)
                )
                duration_secs = cursor.fetchone()[0]
                duration_str = self.format_duration(duration_secs)

                self.send_notification(
                    title=self.get_project_name(cwd),
                    subtitle=f"Task #{seq} complete",
                    message=f"Duration: {duration_str}",
                    sound=NOTIFICATION_SOUND,
                    cwd=cwd,
                    urgency="normal"
                )

                logging.info(f"Task completed: session={session_id}, seq={seq}, duration={duration_str}")

    def handle_subagent_stop(self, data):
        """SubagentStop: Subagent task completed"""
        cwd = data.get("cwd", "")

        self.send_notification(
            title=self.get_project_name(cwd),
            subtitle="Agent task complete",
            message="Subagent finished processing",
            sound=NOTIFICATION_SOUND,
            cwd=cwd,
            urgency="low"
        )

    def handle_notification(self, data):
        """Notification: Handle all notification types with appropriate urgency"""
        notification_type = data.get("notification_type", "")
        message = data.get("message", "Claude Code notification")
        cwd = data.get("cwd", "")
        session_id = data.get("session_id")

        # Map notification types to appropriate handling
        notification_configs = {
            "permission_prompt": {
                "title": "Permission Required",
                "subtitle": "Claude needs approval",
                "message": message,
                "sound": "Basso",  # More urgent sound
                "urgency": "critical",
                "action": "focus"  # Should focus immediately
            },
            "idle_prompt": {
                "title": "Waiting for Input",
                "subtitle": "Claude is idle",
                "message": "Waiting for your input (60+ seconds)",
                "sound": "Purr",  # Gentle sound
                "urgency": "low",
                "action": "focus"
            },
            "elicitation_dialog": {
                "title": "Input Needed",
                "subtitle": "MCP tool requires input",
                "message": message,
                "sound": "Ping",
                "urgency": "high",
                "action": "focus"
            },
            "auth_success": {
                "title": "Authentication Success",
                "subtitle": "Logged in successfully",
                "message": message,
                "sound": "Glass",
                "urgency": "low",
                "action": "none"
            }
        }

        config = notification_configs.get(
            notification_type,
            {
                "title": "Claude Code",
                "subtitle": "Notification",
                "message": message,
                "sound": NOTIFICATION_SOUND,
                "urgency": "normal",
                "action": "focus"
            }
        )

        self.send_notification(
            title=config["title"],
            subtitle=config["subtitle"],
            message=config["message"],
            sound=config["sound"],
            cwd=cwd if config["action"] == "focus" else None,
            urgency=config["urgency"]
        )

        logging.info(f"Notification: type={notification_type}, urgency={config['urgency']}")

    def handle_session_start(self, data):
        """SessionStart: Session started"""
        source = data.get("source", "startup")
        cwd = data.get("cwd", "")

        messages = {
            "startup": "Session started",
            "resume": "Session resumed",
            "clear": "Session cleared",
            "compact": "Session compacted"
        }

        self.send_notification(
            title=self.get_project_name(cwd),
            subtitle=messages.get(source, "Session event"),
            message=f"Ready to work • {datetime.now().strftime('%H:%M')}",
            sound="Glass",
            cwd=None,  # Don't open editor on session start
            urgency="low"
        )

    def handle_session_end(self, data):
        """SessionEnd: Session ended"""
        reason = data.get("reason", "exit")
        cwd = data.get("cwd", "")

        self.send_notification(
            title=self.get_project_name(cwd),
            subtitle="Session ended",
            message=f"Reason: {reason}",
            sound="Glass",
            cwd=None,
            urgency="low"
        )

    # ========================================================================
    # Notification Sending
    # ========================================================================

    def send_notification(self, title, subtitle, message, sound, cwd=None, urgency="normal"):
        """Send notification via terminal-notifier with optional click action"""
        try:
            cmd = [
                "terminal-notifier",
                "-title", title,
                "-subtitle", subtitle,
                "-message", message,
                "-sound", sound,
            ]

            # Add click action to open in editor
            if cwd and EDITOR_COMMAND:
                execute_cmd = self.get_editor_command(cwd)
                if execute_cmd:
                    cmd.extend(["-execute", execute_cmd])

            # Run notification
            subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                timeout=5
            )

            logging.info(f"Sent notification: {title} - {subtitle}")

        except FileNotFoundError:
            # Fallback to osascript if terminal-notifier not found
            try:
                applescript = f'display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "{sound}"'
                subprocess.run(
                    ["osascript", "-e", applescript],
                    check=False,
                    capture_output=True,
                    timeout=5
                )
                logging.info(f"Sent notification via osascript: {title}")
            except Exception as e:
                logging.error(f"Failed to send notification: {e}")
        except Exception as e:
            logging.error(f"Notification error: {e}")

    def get_editor_command(self, cwd):
        """Get the command to open editor at cwd"""
        if not cwd or not EDITOR_COMMAND:
            return None

        # Map editor commands to their open syntax
        editor_cmds = {
            "zed": f'zed "{cwd}"',
            "code": f'/usr/local/bin/code "{cwd}"',
            "cursor": f'cursor "{cwd}"',
            "subl": f'subl "{cwd}"',
            "atom": f'atom "{cwd}"',
        }

        return editor_cmds.get(EDITOR_COMMAND, f'{EDITOR_COMMAND} "{cwd}"')

    # ========================================================================
    # Utilities
    # ========================================================================

    def get_project_name(self, cwd):
        """Extract project name from cwd"""
        if not cwd:
            return "Claude Code"
        return os.path.basename(cwd) or "Claude Code"

    def format_duration(self, seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"


def main():
    """Main entry point - route to appropriate handler"""
    try:
        # Read hook event from command line
        if len(sys.argv) < 2:
            print("Usage: claude-notifier.py <hook_event>")
            print("Available hooks: UserPromptSubmit, Stop, SubagentStop, Notification, SessionStart, SessionEnd")
            sys.exit(1)

        hook_event = sys.argv[1]

        # Read JSON data from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            logging.warning(f"No input data for {hook_event}")
            sys.exit(0)

        data = json.loads(input_data)

        # Validate hook_event_name matches
        if data.get("hook_event_name") != hook_event:
            logging.warning(f"Hook mismatch: expected {hook_event}, got {data.get('hook_event_name')}")

        # Route to handler
        notifier = ClaudeNotifier()

        handlers = {
            "UserPromptSubmit": notifier.handle_user_prompt_submit,
            "Stop": notifier.handle_stop,
            "SubagentStop": notifier.handle_subagent_stop,
            "Notification": notifier.handle_notification,
            "SessionStart": notifier.handle_session_start,
            "SessionEnd": notifier.handle_session_end,
        }

        handler = handlers.get(hook_event)
        if handler:
            handler(data)
        else:
            logging.warning(f"Unknown hook event: {hook_event}")
            sys.exit(1)

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error in {hook_event}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
