#!/usr/bin/env python3
"""
Notification management tool for Claude Code

Manages notification backends, installation, and hooks configuration.
"""

from pathlib import Path
import json
import subprocess
import sys
from typing import Optional
import shutil

try:
    import tomli
    import tomli_w
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("Error: Required dependencies not found. Run: make install", file=sys.stderr)
    sys.exit(1)

# Auto-detect repository location
REPO_DIR = Path(__file__).parent.parent.resolve()
CONFIG_DIR = Path.home() / ".claude" / "configs"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"
NOTIFICATIONS_DIR = REPO_DIR / "shell" / "notifications"
TEMPLATES_DIR = REPO_DIR / "settings"

console = Console()

# Backend definitions
BACKENDS = {
    "terminal-notifier": {
        "name": "terminal-notifier",
        "description": "Simple, cross-platform notifications with sound support",
        "dependencies": ["terminal-notifier (optional - falls back to osascript)"],
        "script": "terminal-notifier.sh",
        "template": "hooks-terminal-notifier.json.tmpl",
        "multi_instance": False,
        "click_to_focus": False,
        "remote_support": False,
    },
    "claude-notifier": {
        "name": "claude-notifier (Recommended)",
        "description": "Comprehensive notifications with task tracking and editor integration",
        "dependencies": ["terminal-notifier (optional - falls back to osascript)"],
        "script": "claude-notifier.py",
        "template": "hooks-claude-notifier.json.tmpl",
        "multi_instance": False,
        "click_to_focus": True,
        "remote_support": False,
    },
    "cc-notifier": {
        "name": "cc-notifier (Advanced)",
        "description": "Multi-instance tracking, requires Hammerspoon",
        "dependencies": ["Hammerspoon", "terminal-notifier", "cc-notifier"],
        "script": "cc-notifier-installer.sh",
        "template": "hooks-cc-notifier.json.tmpl",
        "multi_instance": True,
        "click_to_focus": True,
        "remote_support": True,
    },
}


def list_backends():
    """List available notification backends"""
    console.print("\n[bold blue]Available Notification Backends[/bold blue]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Backend", style="cyan", width=20)
    table.add_column("Description", width=35)
    table.add_column("Multi-Instance", justify="center", width=12)
    table.add_column("Click-to-Focus", justify="center", width=13)
    table.add_column("Remote", justify="center", width=8)

    for backend_id, info in BACKENDS.items():
        table.add_row(
            backend_id,
            info["description"],
            "✅" if info["multi_instance"] else "❌",
            "✅" if info["click_to_focus"] else "❌",
            "✅" if info["remote_support"] else "❌",
        )

    console.print(table)
    console.print("\nUse: [cyan]make notifications-install BACKEND=<backend>[/cyan] to install\n")


def check_dependencies(backend: str) -> bool:
    """Check if backend dependencies are installed"""
    if backend not in BACKENDS:
        console.print(f"[red]Error: Unknown backend '{backend}'[/red]")
        return False

    backend_info = BACKENDS[backend]
    missing = []

    for dep in backend_info["dependencies"]:
        # Skip optional dependencies
        if "(optional" in dep:
            continue

        if dep == "Hammerspoon":
            if not Path("/Applications/Hammerspoon.app").exists():
                missing.append(dep)
        elif dep == "cc-notifier":
            if not Path.home().joinpath(".cc-notifier", "cc-notifier").exists():
                missing.append(dep)
        else:
            # Check if command exists
            if shutil.which(dep) is None:
                missing.append(dep)

    if missing:
        console.print(f"[yellow]Missing dependencies for {backend}:[/yellow]")
        for dep in missing:
            console.print(f"  - {dep}")
        return False

    console.print(f"[green]All dependencies for {backend} are installed[/green]")
    return True


def install_backend(backend: str):
    """Install a notification backend"""
    if backend not in BACKENDS:
        console.print(f"[red]Error: Unknown backend '{backend}'[/red]")
        console.print("Available backends:", ", ".join(BACKENDS.keys()))
        sys.exit(1)

    backend_info = BACKENDS[backend]
    console.print(f"\n[bold blue]Installing {backend_info['name']}[/bold blue]\n")

    # Special handling for cc-notifier (runs installer script)
    if backend == "cc-notifier":
        installer_script = NOTIFICATIONS_DIR / "cc-notifier-installer.sh"
        if not installer_script.exists():
            console.print(f"[red]Error: Installer script not found: {installer_script}[/red]")
            sys.exit(1)

        console.print("Running cc-notifier installer...")
        try:
            subprocess.run([str(installer_script)], check=True)
            console.print(f"\n[green]✓ {backend} installed successfully[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error installing {backend}: {e}[/red]")
            sys.exit(1)
    else:
        # Check dependencies
        if not check_dependencies(backend):
            console.print(f"\n[yellow]Install missing dependencies:[/yellow]")
            if backend == "terminal-notifier":
                console.print("  brew install terminal-notifier")
            sys.exit(1)

        console.print(f"[green]✓ {backend} is ready to use[/green]")

    console.print(f"\nNext step: [cyan]make notifications-enable BACKEND={backend}[/cyan]")


def load_settings() -> dict:
    """Load current settings.json"""
    if not SETTINGS_FILE.exists():
        return {}

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


def save_settings(settings: dict):
    """Save settings.json"""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_current_config() -> dict:
    """Load current mode configuration with personal overrides"""
    mode_file = CONFIG_DIR / "current_mode"
    if not mode_file.exists():
        console.print("[yellow]No active mode. Run: make switch MODE=anthropic[/yellow]")
        return {}

    mode = mode_file.read_text().strip()
    config_file = REPO_DIR / "configs" / f"{mode}.toml"

    # Load base config
    with open(config_file, "rb") as f:
        config = tomli.load(f)

    # Merge personal overrides
    personal_path = CONFIG_DIR / "personal.toml"
    if personal_path.exists():
        with open(personal_path, "rb") as f:
            personal = tomli.load(f)

        # Deep merge
        for section, values in personal.items():
            if section in config:
                config[section].update(values)
            else:
                config[section] = values

    return config


def enable_hooks(backend: str):
    """Enable notification hooks for a backend"""
    if backend not in BACKENDS:
        console.print(f"[red]Error: Unknown backend '{backend}'[/red]")
        sys.exit(1)

    backend_info = BACKENDS[backend]
    template_file = TEMPLATES_DIR / backend_info["template"]

    if not template_file.exists():
        console.print(f"[red]Error: Template not found: {template_file}[/red]")
        sys.exit(1)

    # Load template
    with open(template_file, "r") as f:
        template = json.load(f)

    # Load current config for variable substitution
    config = load_current_config()
    notification_config = config.get("notifications", {})

    # Substitute variables
    template_str = json.dumps(template)
    template_str = template_str.replace("${REPO_DIR}", str(REPO_DIR))
    template_str = template_str.replace("${NOTIFICATION_SOUND}", notification_config.get("sound", "Glass"))
    template_str = template_str.replace("${NOTIFICATION_EDITOR}", notification_config.get("editor", "zed"))
    template_str = template_str.replace("${PUSHOVER_API_TOKEN}", notification_config.get("pushover_api_token", ""))
    template_str = template_str.replace("${PUSHOVER_USER_KEY}", notification_config.get("pushover_user_key", ""))

    template = json.loads(template_str)

    # Load existing settings
    settings = load_settings()

    # Merge hooks
    if "hooks" not in settings:
        settings["hooks"] = {}

    for hook_type, hooks in template["hooks"].items():
        if hook_type not in settings["hooks"]:
            settings["hooks"][hook_type] = []
        settings["hooks"][hook_type].extend(hooks)

    # Merge env vars
    if "env" in template:
        if "env" not in settings:
            settings["env"] = {}
        settings["env"].update(template["env"])

    # Save settings
    save_settings(settings)

    console.print(f"\n[green]✓ Notification hooks enabled for {backend}[/green]")
    console.print(f"Settings updated: {SETTINGS_FILE}")
    console.print("\nTest with: [cyan]make notifications-test[/cyan]")


def disable_hooks():
    """Disable all notification hooks"""
    settings = load_settings()

    if "hooks" not in settings:
        console.print("[yellow]No hooks configured[/yellow]")
        return

    # Remove notification-related hooks
    notification_hooks = ["Stop", "SubagentStop", "Notification", "SessionStart", "SessionEnd", "PermissionRequest"]

    for hook_type in notification_hooks:
        if hook_type in settings["hooks"]:
            # Filter out notification hooks (those containing our scripts)
            settings["hooks"][hook_type] = [
                hook for hook in settings["hooks"][hook_type]
                if not any(
                    "cc-notifier" in str(h.get("command", ""))
                    or "osascript-notifier" in str(h.get("command", ""))
                    or "terminal-notifier.sh" in str(h.get("command", ""))
                    or "claude-notifier.py" in str(h.get("command", ""))
                    for h in hook.get("hooks", [])
                )
            ]

            # Remove empty hook arrays
            if not settings["hooks"][hook_type]:
                del settings["hooks"][hook_type]

    save_settings(settings)
    console.print("[green]✓ Notification hooks disabled[/green]")


def test_notification(backend: Optional[str] = None):
    """Send a test notification"""
    # Auto-detect backend from config if not specified
    if backend is None:
        config = load_current_config()
        backend = config.get("notifications", {}).get("backend", "terminal-notifier")

    if backend not in BACKENDS:
        console.print(f"[red]Error: Unknown backend '{backend}'[/red]")
        sys.exit(1)

    console.print(f"Sending test notification using {backend}...")

    # Create test JSON input
    if backend == "claude-notifier":
        test_input = json.dumps({
            "hook_event_name": "Stop",
            "session_id": "test-session",
            "cwd": str(Path.cwd()),
        })
    else:
        test_input = json.dumps({"type": "Stop", "workingDirectory": str(Path.cwd())})

    if backend == "cc-notifier":
        console.print("[yellow]Note: cc-notifier requires a Claude session to be initialized first.[/yellow]\n")
        script = Path.home() / ".cc-notifier" / "cc-notifier"
        args = ["notify"]
    elif backend == "claude-notifier":
        script = NOTIFICATIONS_DIR / BACKENDS[backend]["script"]
        args = ["Stop"]  # Test with Stop event
    else:
        # terminal-notifier
        script = NOTIFICATIONS_DIR / BACKENDS[backend]["script"]
        args = []

    if not script.exists():
        console.print(f"[red]Error: Script not found: {script}[/red]")
        console.print(f"Run: [cyan]make notifications-install BACKEND={backend}[/cyan]")
        sys.exit(1)

    try:
        subprocess.run(
            [str(script)] + args,
            input=test_input,
            text=True,
            check=True,
            capture_output=True
        )
        console.print("[green]✓ Test notification sent[/green]")
        console.print("\nYou should see a notification appear on your screen!")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error sending notification: {e}[/red]")
        if e.stderr:
            console.print(f"[yellow]stderr: {e.stderr}[/yellow]")

        if backend == "cc-notifier":
            console.print("\n[yellow]This is expected if you haven't started a Claude session yet.[/yellow]")
            console.print("[cyan]To test properly:[/cyan]")
            console.print("  1. Start a new Claude Code session: claude")
            console.print("  2. Give Claude a task")
            console.print("  3. Switch to another window")
            console.print("  4. When Claude finishes, you'll get a notification")
        else:
            console.print("\n[yellow]Check if terminal-notifier is installed:[/yellow]")
            console.print("  brew install terminal-notifier")


def show_status():
    """Show current notification configuration status"""
    console.print("\n[bold blue]Notification System Status[/bold blue]\n")

    # Check current mode
    mode_file = CONFIG_DIR / "current_mode"
    if mode_file.exists():
        mode = mode_file.read_text().strip()
        console.print(f"Current mode: [cyan]{mode}[/cyan]")

        # Load config
        config = load_current_config()
        if "notifications" in config:
            notif_config = config["notifications"]
            console.print(f"Backend: [cyan]{notif_config.get('backend', 'not set')}[/cyan]")
            console.print(f"Sound: [cyan]{notif_config.get('sound', 'not set')}[/cyan]")
    else:
        console.print("[yellow]No active mode configured[/yellow]")

    # Check settings
    settings = load_settings()
    if "hooks" in settings:
        notification_hooks = ["Stop", "SubagentStop", "Notification", "SessionStart", "SessionEnd"]
        enabled_hooks = [h for h in notification_hooks if h in settings["hooks"]]

        if enabled_hooks:
            console.print(f"\nEnabled hooks: [green]{', '.join(enabled_hooks)}[/green]")
        else:
            console.print("\n[yellow]No notification hooks enabled[/yellow]")
    else:
        console.print("\n[yellow]No hooks configured[/yellow]")

    console.print()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        console.print("[red]Usage: notifications.py <command> [args][/red]")
        console.print("\nCommands:")
        console.print("  list              - List available backends")
        console.print("  install <backend> - Install a backend")
        console.print("  enable <backend>  - Enable hooks for a backend")
        console.print("  disable           - Disable all notification hooks")
        console.print("  test [backend]    - Send a test notification")
        console.print("  status            - Show current configuration")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_backends()
    elif command == "install":
        if len(sys.argv) < 3:
            console.print("[red]Error: Backend name required[/red]")
            console.print("Example: notifications.py install osascript")
            sys.exit(1)
        install_backend(sys.argv[2])
    elif command == "enable":
        if len(sys.argv) < 3:
            console.print("[red]Error: Backend name required[/red]")
            console.print("Example: notifications.py enable osascript")
            sys.exit(1)
        enable_hooks(sys.argv[2])
    elif command == "disable":
        disable_hooks()
    elif command == "test":
        backend = sys.argv[2] if len(sys.argv) > 2 else None
        test_notification(backend)
    elif command == "status":
        show_status()
    else:
        console.print(f"[red]Error: Unknown command '{command}'[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
