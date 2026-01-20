# Settings

This directory contains settings.json templates for Claude Code.

## Structure

```
settings/
├── hooks-terminal-notifier.json.tmpl   # Simple notification hooks
├── hooks-claude-notifier.json.tmpl     # Comprehensive notification system (Recommended)
├── hooks-cc-notifier.json.tmpl         # Advanced multi-instance tracking
├── global.json.tmpl                    # Global settings template
├── project.json.tmpl                   # Project-specific template
└── README.md
```

## Notification System

### Available Backends

| Backend | Description | Dependencies | Features |
|---------|-------------|--------------|----------|
| **claude-notifier** (Recommended) | Comprehensive notifications with task tracking and editor integration | terminal-notifier (optional) | Task duration, job numbering, click-to-open editor, different sounds per urgency |
| **terminal-notifier** | Simple cross-platform notifications | terminal-notifier (optional) | Basic notifications with sound support |
| **cc-notifier** | Advanced multi-instance tracking | Hammerspoon, terminal-notifier, cc-notifier | Window tracking, click-to-focus across Spaces, remote SSH support |

### Notification Types (claude-notifier)

| Hook Event | Notification Type | Title | Sound | Urgency | Click Action | When It Fires |
|------------|------------------|-------|-------|---------|--------------|---------------|
| **UserPromptSubmit** | - | - | - | - | - | Records task start time (no notification) |
| **Stop** | Task Complete | `<project-name>` | Glass | Normal | Opens editor at project dir | When Claude finishes responding to your prompt |
| **SubagentStop** | Agent Complete | `<project-name>` | Glass | Low | Opens editor | When a subagent (code-reviewer, etc.) finishes |
| **Notification** `permission_prompt` | Permission Required | Permission Required | Basso | Critical | Opens editor | When Claude needs permission for a tool |
| **Notification** `idle_prompt` | Waiting for Input | Waiting for Input | Purr | Low | Opens editor | When Claude waits 60+ seconds for input |
| **Notification** `elicitation_dialog` | Input Needed | Input Needed | Ping | High | Opens editor | When MCP tool requires user input |
| **Notification** `auth_success` | Authentication Success | Authentication Success | Glass | Low | No action | When login/auth succeeds |
| **SessionStart** | Session Started | `<project-name>` | Glass | Low | No action | When Claude Code session starts |
| **SessionEnd** | Session Ended | `<project-name>` | Glass | Low | No action | When Claude Code session ends |

### Sound Guide (macOS)

| Sound | Character | Best For |
|-------|-----------|----------|
| **Basso** | Deep, attention-grabbing | Critical alerts (permissions) |
| **Ping** | Sharp, clear | High priority (input needed) |
| **Glass** | Pleasant, balanced | Normal completion notifications |
| **Purr** | Soft, gentle | Low priority (idle, waiting) |
| **Submarine** | Sonar-like | Alternative attention sound |
| **Frog** | Quirky | Alternative normal sound |

### Task Duration Display

The Stop event shows task duration in notification subtitle:

- `<60s`: "42s"
- `60s-3600s`: "5m 23s"
- `>3600s`: "2h 15m"

Example: "Task #3 complete - Duration: 2m 15s"

### Configuration

Configure in `~/.claude/configs/personal.toml`:

```toml
[notifications]
backend = "claude-notifier"  # terminal-notifier, claude-notifier, cc-notifier
sound = "Glass"              # Default sound (can be overridden per notification type)
editor = "zed"               # zed, code, cursor, subl, atom
```

Supported editors for click-to-open:
- `zed` - Zed editor
- `code` - VS Code
- `cursor` - Cursor editor
- `subl` - Sublime Text
- `atom` - Atom editor

### Installation

```bash
# List available backends
make notifications-list

# Install claude-notifier (recommended)
make notifications-install BACKEND=claude-notifier

# Enable hooks
make notifications-enable BACKEND=claude-notifier

# Test it
make notifications-test

# Check status
make notifications-status
```

### How It Works

1. **UserPromptSubmit Hook**: Records start time and session info in SQLite database
2. **Stop Hook**: Calculates duration, retrieves job sequence number, sends notification with duration
3. **Notification Hook**: Detects notification type from JSON, applies appropriate sound/urgency
4. **Click Action**: Clicking notification runs editor command to open project directory

### Session Tracking

claude-notifier maintains a SQLite database at `~/.claude/notifier/sessions.db`:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    created_at DATETIME,
    prompt TEXT,
    cwd TEXT,
    seq INTEGER,          -- Job #1, #2, #3, etc. per session
    completed_at DATETIME,
    duration_seconds INTEGER
);
```

Logs are stored at `~/.claude/notifier/notifier.log` with daily rotation (7 day retention).

### Fallback Behavior

If `terminal-notifier` is not installed:
1. Falls back to native macOS `osascript` notifications
2. All functionality works except click-to-open editor
3. Install terminal-notifier for full functionality: `brew install terminal-notifier`

### Troubleshooting

**Notification doesn't appear:**
```bash
# Check if hooks are enabled
make notifications-status

# Test notification
make notifications-test

# Check logs
tail -f ~/.claude/notifier/notifier.log
```

**Editor doesn't open on click:**
- Requires `terminal-notifier` installed
- Verify editor is in PATH: `which zed`
- Check `NOTIFICATION_EDITOR` env var matches your editor

**Wrong sound playing:**
- Check personal.toml: `backend = "claude-notifier"`
- Sounds are hardcoded per urgency level in claude-notifier.py:149-227
- Override default sound in personal.toml

---

## Using Settings Templates

```bash
# View differences between template and current
make settings-diff

# Apply settings template
make settings-apply
```

## Template Variables

Settings templates use Jinja2 variables for customization:

```json
{
  "apiKey": "{{ AWS_PROFILE }}",
  "model": "{{ ANTHROPIC_MODEL }}"
}
```

Variables are replaced from:
1. Environment variables
2. Personal config (`~/.claude/configs/personal.toml`)
3. Current mode config

## Hook Templates

Notification hook templates support these variables:

- `${REPO_DIR}` - Repository directory path
- `${NOTIFICATION_SOUND}` - Sound from config (e.g., "Glass")
- `${NOTIFICATION_EDITOR}` - Editor from config (e.g., "zed")
- `${PUSHOVER_API_TOKEN}` - Pushover token (cc-notifier only)
- `${PUSHOVER_USER_KEY}` - Pushover user key (cc-notifier only)

## Creating Templates

1. Create `.json.tmpl` file in `settings/`
2. Use `{{ VARIABLE }}` for dynamic values
3. Add documentation in comments (JSON5 style)
4. Commit to repo for sharing

## Settings Location

Claude Code settings are typically in:
- Global: `~/.claude/settings.json`
- Project: `.claude/settings.json`

## Example Template

```json
{
  // Model configuration
  "defaultModel": "{{ ANTHROPIC_MODEL }}",

  // Performance settings
  "disablePromptCaching": {{ DISABLE_PROMPT_CACHING | default(false) }},

  // Optional features
  "disableTelemetry": {{ DISABLE_TELEMETRY | default(false) }}
}
```

## Usage

Settings templates help maintain consistent configuration across:
- Multiple machines
- Team members
- Different projects

Update templates in repo, apply with `make settings:apply`.
