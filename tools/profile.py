#!/usr/bin/env python3
"""
Claude Code Profile Manager

Enables switching between multiple Claude Code profiles with different
skills, agents, hooks, and MCP servers.

Usage:
    python tools/profile.py list                    # List all profiles
    python tools/profile.py create <name>           # Create new profile
    python tools/profile.py switch <name>           # Switch to profile
    python tools/profile.py clone <src> <dest>      # Clone a profile
    python tools/profile.py status                  # Show active profile
    python tools/profile.py backup <name>           # Backup a profile
    python tools/profile.py migrate                 # Migrate ~/.claude to profile system
"""

import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt

console = Console()

PROFILES_DIR = Path.home() / ".claude-profiles"
DEFAULT_CLAUDE_DIR = Path.home() / ".claude"


def ensure_profiles_dir():
    """Create profiles directory if it doesn't exist"""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def get_profile_path(name: str) -> Path:
    """Get path to a profile directory"""
    return PROFILES_DIR / name


def get_current_profile() -> Optional[str]:
    """Get the name of the currently active profile"""
    current_link = PROFILES_DIR / "current"
    if current_link.exists() and current_link.is_symlink():
        target = current_link.resolve()
        return target.name
    return None


def list_profiles():
    """List all available profiles"""
    ensure_profiles_dir()

    profiles = [p for p in PROFILES_DIR.iterdir()
                if p.is_dir() and p.name != "backups"]

    if not profiles:
        console.print("[yellow]No profiles found. Create one with:[/yellow]")
        console.print("  python tools/profile.py create <name>")
        return

    current = get_current_profile()

    table = Table(title="Claude Code Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Active", style="green")
    table.add_column("Skills", justify="right")
    table.add_column("Agents", justify="right")
    table.add_column("Hooks", justify="right")
    table.add_column("MCP", justify="right")

    for profile in sorted(profiles):
        is_active = "✓" if profile.name == current else ""

        # Count items
        skills = len(list((profile / "skills").glob("*"))) if (profile / "skills").exists() else 0
        agents = len(list((profile / "agents").glob("*.md"))) if (profile / "agents").exists() else 0
        hooks = len(list((profile / "hooks").glob("*.ts"))) if (profile / "hooks").exists() else 0
        mcp_count = 0
        settings = profile / "settings.json"
        if settings.exists():
            try:
                with open(settings) as f:
                    data = json.load(f)
                    mcp_count = len(data.get("mcpServers", {}))
            except:
                pass

        table.add_row(
            profile.name,
            is_active,
            str(skills),
            str(agents),
            str(hooks),
            str(mcp_count)
        )

    console.print(table)

    if current:
        console.print(f"\n[bold green]Active profile:[/bold green] {current}")
        console.print(f"[dim]CLAUDE_CONFIG_DIR should be: {get_profile_path(current)}[/dim]")


def create_profile(name: str, template: Optional[str] = None):
    """Create a new profile"""
    ensure_profiles_dir()

    profile_path = get_profile_path(name)

    if profile_path.exists():
        console.print(f"[red]Profile '{name}' already exists[/red]")
        return False

    console.print(f"Creating profile: [cyan]{name}[/cyan]")

    # Create directory structure
    profile_path.mkdir(parents=True)
    (profile_path / "skills").mkdir()
    (profile_path / "agents").mkdir()
    (profile_path / "hooks").mkdir()
    (profile_path / "mcp" / "servers").mkdir(parents=True)

    # Create minimal settings.json
    settings = {
        "mcpServers": {},
        "env": {}
    }

    with open(profile_path / "settings.json", "w") as f:
        json.dump(settings, f, indent=2)

    console.print(f"[green]✓[/green] Created profile at {profile_path}")

    # Ask if they want to switch to it
    if Confirm.ask("Switch to this profile now?"):
        switch_profile(name)

    return True


def switch_profile(name: str):
    """Switch to a different profile"""
    ensure_profiles_dir()

    profile_path = get_profile_path(name)

    if not profile_path.exists():
        console.print(f"[red]Profile '{name}' does not exist[/red]")
        console.print("Available profiles:")
        list_profiles()
        return False

    current_link = PROFILES_DIR / "current"

    # Remove old symlink
    if current_link.exists():
        current_link.unlink()

    # Create new symlink
    current_link.symlink_to(profile_path)

    console.print(f"[green]✓[/green] Switched to profile: [cyan]{name}[/cyan]")
    console.print(f"\nTo activate, add to your shell config (~/.zshrc or ~/.bashrc):")
    console.print(f"[yellow]export CLAUDE_CONFIG_DIR={profile_path}[/yellow]")
    console.print("\nOr for temporary use:")
    console.print(f"[yellow]export CLAUDE_CONFIG_DIR={profile_path} && claude[/yellow]")

    return True


def clone_profile(src: str, dest: str):
    """Clone an existing profile"""
    ensure_profiles_dir()

    src_path = get_profile_path(src)
    dest_path = get_profile_path(dest)

    if not src_path.exists():
        console.print(f"[red]Source profile '{src}' does not exist[/red]")
        return False

    if dest_path.exists():
        console.print(f"[red]Destination profile '{dest}' already exists[/red]")
        return False

    console.print(f"Cloning [cyan]{src}[/cyan] → [cyan]{dest}[/cyan]")
    shutil.copytree(src_path, dest_path)

    console.print(f"[green]✓[/green] Cloned profile successfully")

    if Confirm.ask("Switch to the new profile?"):
        switch_profile(dest)

    return True


def status():
    """Show current profile status"""
    current = get_current_profile()

    if not current:
        console.print("[yellow]No profile is currently active[/yellow]")
        console.print("Create a profile with: python tools/profile.py create <name>")
        return

    profile_path = get_profile_path(current)

    console.print(f"[bold green]Active Profile:[/bold green] {current}")
    console.print(f"[bold]Location:[/bold] {profile_path}")

    # Check if CLAUDE_CONFIG_DIR is set correctly
    import os
    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")

    if env_dir:
        if Path(env_dir).resolve() == profile_path:
            console.print("[green]✓[/green] CLAUDE_CONFIG_DIR is set correctly")
        else:
            console.print(f"[yellow]⚠[/yellow] CLAUDE_CONFIG_DIR is set to: {env_dir}")
            console.print(f"[yellow]  Expected: {profile_path}[/yellow]")
    else:
        console.print("[yellow]⚠[/yellow] CLAUDE_CONFIG_DIR is not set")
        console.print(f"[yellow]  Add to shell: export CLAUDE_CONFIG_DIR={profile_path}[/yellow]")

    # Show profile contents
    table = Table(title="Profile Contents")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Examples", style="dim")

    # Skills
    skills_dir = profile_path / "skills"
    if skills_dir.exists():
        skills = list(skills_dir.glob("*"))
        examples = ", ".join([s.name for s in skills[:3]])
        if len(skills) > 3:
            examples += f" (+{len(skills)-3} more)"
        table.add_row("Skills", str(len(skills)), examples)

    # Agents
    agents_dir = profile_path / "agents"
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.md"))
        examples = ", ".join([a.stem for a in agents[:3]])
        if len(agents) > 3:
            examples += f" (+{len(agents)-3} more)"
        table.add_row("Agents", str(len(agents)), examples)

    # Hooks
    hooks_dir = profile_path / "hooks"
    if hooks_dir.exists():
        hooks = list(hooks_dir.glob("*.ts"))
        examples = ", ".join([h.stem for h in hooks[:3]])
        if len(hooks) > 3:
            examples += f" (+{len(hooks)-3} more)"
        table.add_row("Hooks", str(len(hooks)), examples)

    # MCP
    settings = profile_path / "settings.json"
    if settings.exists():
        try:
            with open(settings) as f:
                data = json.load(f)
                mcp_servers = data.get("mcpServers", {})
                examples = ", ".join(list(mcp_servers.keys())[:3])
                if len(mcp_servers) > 3:
                    examples += f" (+{len(mcp_servers)-3} more)"
                table.add_row("MCP Servers", str(len(mcp_servers)), examples)
        except:
            pass

    console.print(table)


def backup_profile(name: str):
    """Backup a profile"""
    ensure_profiles_dir()

    profile_path = get_profile_path(name)

    if not profile_path.exists():
        console.print(f"[red]Profile '{name}' does not exist[/red]")
        return False

    backups_dir = PROFILES_DIR / "backups"
    backups_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{name}_{timestamp}"
    backup_path = backups_dir / backup_name

    console.print(f"Backing up [cyan]{name}[/cyan]...")
    shutil.copytree(profile_path, backup_path)

    console.print(f"[green]✓[/green] Backup saved to {backup_path}")

    # Keep only last 5 backups for this profile
    profile_backups = sorted([b for b in backups_dir.glob(f"{name}_*")],
                            key=lambda x: x.name, reverse=True)

    for old_backup in profile_backups[5:]:
        console.print(f"[dim]Removing old backup: {old_backup.name}[/dim]")
        shutil.rmtree(old_backup)

    return True


def migrate_from_claude(mode: str = "full"):
    """Migrate existing ~/.claude to profile system

    Args:
        mode: 'full' = everything, 'clean' = only config/code, 'selective' = ask
    """
    if not DEFAULT_CLAUDE_DIR.exists():
        console.print("[yellow]No ~/.claude directory found[/yellow]")
        return False

    ensure_profiles_dir()

    # Check if already migrated
    default_profile = get_profile_path("default")
    if default_profile.exists():
        console.print("[yellow]Profile 'default' already exists[/yellow]")
        if not Confirm.ask("Overwrite with current ~/.claude contents?"):
            return False
        shutil.rmtree(default_profile)

    # Define what to copy
    ESSENTIAL = {
        "skills", "agents", "hooks", "rules", "configs",
        "settings.json", "mcp", "servers", "scripts",
        "plugins", "runtime", "state", ".env"
    }

    SESSION_DATA = {
        "debug", "file-history", "history.jsonl", "todos",
        "session-env", "cache", "paste-cache", "shell-snapshots",
        ".coordination-session-id", "sessions", "projects",
        "plans", "downloads", "statsig", "stats-cache.json",
        "autocompact.log", "excalidraw.log"
    }

    # Ask user what to copy
    if mode == "selective":
        console.print("\n[bold]What to migrate?[/bold]")
        console.print("1. Essential only (skills, agents, hooks, rules, settings)")
        console.print("2. Essential + session data (history, cache, debug logs)")
        console.print("3. Everything (complete copy)")

        choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")

        if choice == "1":
            mode = "clean"
        elif choice == "2":
            mode = "full"
        else:
            mode = "full"

    console.print(f"Migrating [cyan]~/.claude[/cyan] → [cyan]~/.claude-profiles/default[/cyan]")
    console.print(f"Mode: [yellow]{mode}[/yellow]")

    # Create profile directory
    default_profile.mkdir(parents=True, exist_ok=True)

    if mode == "full":
        # Copy everything
        console.print("Copying all files...")
        for item in DEFAULT_CLAUDE_DIR.iterdir():
            if item.name == ".DS_Store":
                continue

            dest = default_profile / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest)

    else:  # clean mode
        # Copy only essential items
        console.print("Copying essential files...")
        for item_name in ESSENTIAL:
            src = DEFAULT_CLAUDE_DIR / item_name
            if not src.exists():
                continue

            dest = default_profile / item_name
            console.print(f"  • {item_name}")

            if src.is_dir():
                shutil.copytree(src, dest, symlinks=True)
            else:
                shutil.copy2(src, dest)

    console.print("[green]✓[/green] Migration complete")

    # Show what was skipped if clean mode
    if mode == "clean":
        skipped = [item for item in SESSION_DATA
                  if (DEFAULT_CLAUDE_DIR / item).exists()]
        if skipped:
            console.print("\n[dim]Skipped session data (not needed for profiles):[/dim]")
            for item in skipped[:5]:
                console.print(f"[dim]  • {item}[/dim]")
            if len(skipped) > 5:
                console.print(f"[dim]  ... and {len(skipped)-5} more[/dim]")

    # Switch to the new profile
    switch_profile("default")

    console.print("\n[bold yellow]Important:[/bold yellow]")
    console.print("Your original ~/.claude is still intact.")
    console.print("To use the profile system, add to your shell config:")
    console.print(f"[yellow]export CLAUDE_CONFIG_DIR={default_profile}[/yellow]")

    return True


def main():
    if len(sys.argv) < 2:
        console.print("Claude Code Profile Manager\n")
        console.print("Usage:")
        console.print("  python tools/profile.py list                    # List all profiles")
        console.print("  python tools/profile.py create <name>           # Create new profile")
        console.print("  python tools/profile.py switch <name>           # Switch to profile")
        console.print("  python tools/profile.py clone <src> <dest>      # Clone a profile")
        console.print("  python tools/profile.py status                  # Show active profile")
        console.print("  python tools/profile.py backup <name>           # Backup a profile")
        console.print("  python tools/profile.py migrate                 # Migrate ~/.claude")
        return

    command = sys.argv[1]

    if command == "list":
        list_profiles()

    elif command == "create":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python tools/profile.py create <name>[/red]")
            return
        create_profile(sys.argv[2])

    elif command == "switch":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python tools/profile.py switch <name>[/red]")
            return
        switch_profile(sys.argv[2])

    elif command == "clone":
        if len(sys.argv) < 4:
            console.print("[red]Usage: python tools/profile.py clone <src> <dest>[/red]")
            return
        clone_profile(sys.argv[2], sys.argv[3])

    elif command == "status":
        status()

    elif command == "backup":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python tools/profile.py backup <name>[/red]")
            return
        backup_profile(sys.argv[2])

    elif command == "migrate":
        mode = sys.argv[2] if len(sys.argv) > 2 else "selective"
        migrate_from_claude(mode)

    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        main()


if __name__ == "__main__":
    main()
