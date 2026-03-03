#!/usr/bin/env python3
"""Claude Code configuration management"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import tomli
import tomli_w
from rich.console import Console
from rich.table import Table

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
# Auto-detect repo location (tools/ is one level down from repo root)
REPO_DIR = Path(__file__).parent.parent.resolve()


def get_active_profile_dir() -> Optional[Path]:
    """Detect active profile directory from CLAUDE_CONFIG_DIR or current symlink"""
    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.exists():
            return p.resolve()

    current_link = Path.home() / ".claude-profiles" / "current"
    if current_link.exists() and current_link.is_symlink():
        return current_link.resolve()

    return None


def load_config(mode: str) -> Dict[str, Any]:
    """Load mode config with personal overrides"""
    base_path = REPO_DIR / f"configs/{mode}.toml"
    with open(base_path, "rb") as f:
        config = tomli.load(f)

    personal_path = CONFIG_DIR / "personal.toml"
    if personal_path.exists():
        with open(personal_path, "rb") as f:
            personal = tomli.load(f)

        for section, values in personal.items():
            if section in config:
                config[section].update(values)
            else:
                config[section] = values

    return config


def _build_env_vars(config: Dict[str, Any]) -> Dict[str, str]:
    """Build env var dict from config"""
    mode = config["mode"]
    models = config["models"]
    performance = config.get("performance", {})
    optional = config.get("optional", {})

    env_vars: Dict[str, str] = {}
    env_vars["CLAUDE_CODE_USE_BEDROCK"] = "1" if mode["use_bedrock"] else "0"
    env_vars["ANTHROPIC_MODEL"] = models["primary"]
    env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = models["haiku"]
    env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] = models["sonnet"]
    env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] = models["opus"]
    env_vars["CLAUDE_CODE_SUBAGENT_MODEL"] = models["subagent"]

    if mode["use_bedrock"] and "aws" in config:
        env_vars["AWS_REGION"] = config["aws"]["region"]
        env_vars["AWS_PROFILE"] = config["aws"]["profile"]

    if performance.get("max_thinking_tokens"):
        env_vars["MAX_THINKING_TOKENS"] = str(performance["max_thinking_tokens"])

    if performance.get("disable_prompt_caching"):
        env_vars["DISABLE_PROMPT_CACHING"] = "1"

    if optional.get("disable_telemetry"):
        env_vars["DISABLE_TELEMETRY"] = "1"

    if optional.get("playwright_headless") is False:
        env_vars["PLAYWRIGHT_HEADLESS"] = "false"

    return env_vars


def apply_config(config: Dict[str, Any], dry_run: bool = False) -> None:
    """Apply config — to active profile's settings.json, or legacy .env file"""
    profile_dir = get_active_profile_dir()
    env_vars = _build_env_vars(config)

    if profile_dir:
        _apply_to_profile(env_vars, config["mode"]["name"], profile_dir, dry_run)
    else:
        _apply_to_env_file(env_vars, config["mode"]["name"], dry_run)


def _apply_to_profile(
    env_vars: Dict[str, str],
    mode_name: str,
    profile_dir: Path,
    dry_run: bool,
) -> None:
    """Merge model env vars into profile's settings.json env block"""
    settings_path = profile_dir / "settings.json"

    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)
    else:
        settings = {"mcpServers": {}, "env": {}}

    if dry_run:
        console.print(f"\n[dim]Would update {settings_path}:[/dim]")
        for k, v in env_vars.items():
            console.print(f"  {k}={v}")
        return

    existing_env = settings.get("env", {})
    existing_env.update(env_vars)
    settings["env"] = existing_env

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    console.print(f"[green]Applied {mode_name} config → {settings_path}[/green]")
    console.print(f"[dim]  Profile: {profile_dir.name}[/dim]")


def _apply_to_env_file(
    env_vars: Dict[str, str],
    mode_name: str,
    dry_run: bool,
) -> None:
    """Legacy: write to ~/.claude/configs/<mode>.env (no active profile)"""
    exports = [f"export {k}='{v}'" for k, v in env_vars.items()]
    script = "\n".join(exports)

    if dry_run:
        console.print(script)
    else:
        out_file = CONFIG_DIR / f"{mode_name}.env"
        out_file.write_text(script)
        console.print(f"[green]Applied {mode_name} config to {out_file}[/green]")


def status() -> None:
    """Show current config status"""
    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[red]No mode configured[/red]")
        return

    mode = current_mode_file.read_text().strip()
    config = load_config(mode)
    profile_dir = get_active_profile_dir()

    table = Table(title="Claude Code Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    if profile_dir:
        table.add_row("Profile", profile_dir.name)
        table.add_row("Profile Dir", str(profile_dir))
    else:
        table.add_row("Profile", "[dim]none (legacy mode)[/dim]")

    table.add_row("Mode", mode)
    table.add_row("Bedrock", str(config["mode"]["use_bedrock"]))
    table.add_row("Primary Model", config["models"]["primary"])
    table.add_row("Subagent Model", config["models"]["subagent"])

    if config["mode"]["use_bedrock"]:
        table.add_row("AWS Region", config.get("aws", {}).get("region", "N/A"))
        table.add_row("AWS Profile", config.get("aws", {}).get("profile", "N/A"))

    console.print(table)


def sync_profile() -> None:
    """Re-apply current mode config to the active profile's settings.json"""
    profile_dir = get_active_profile_dir()
    if not profile_dir:
        console.print("[yellow]No active profile detected.[/yellow]")
        console.print("[dim]Set CLAUDE_CONFIG_DIR or use 'ccp <name>' first.[/dim]")
        console.print("[dim]Falling back to legacy .env mode...[/dim]")

    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[red]No mode configured. Run: make install[/red]")
        return

    mode = current_mode_file.read_text().strip()

    if profile_dir:
        console.print(
            f"Syncing [cyan]{mode}[/cyan] config → "
            f"profile [cyan]{profile_dir.name}[/cyan]"
        )
    else:
        console.print(f"Syncing [cyan]{mode}[/cyan] config → legacy .env")

    config = load_config(mode)
    apply_config(config)
    console.print()
    status()


def switch_mode(mode: str) -> None:
    """Switch to a different mode and apply to active profile or .env"""
    if mode not in ["anthropic", "bedrock"]:
        console.print(f"[red]Invalid mode: {mode}[/red]")
        console.print("Available: anthropic, bedrock")
        sys.exit(1)

    config = load_config(mode)
    apply_config(config)

    current_mode_file = CONFIG_DIR / "current_mode"
    current_mode_file.write_text(mode)

    console.print(f"[green]Switched to {mode} mode[/green]")
    status()


def switch_interactive() -> None:
    """Interactive mode switching — prompts to flip to other mode"""
    from rich.prompt import Confirm

    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[yellow]No mode configured. Run: make install[/yellow]")
        sys.exit(1)

    current_mode = current_mode_file.read_text().strip()
    other_mode = "bedrock" if current_mode == "anthropic" else "anthropic"

    console.print(f"\n[cyan]Current mode:[/cyan] {current_mode}")
    console.print(f"[cyan]Switch to:[/cyan] {other_mode}\n")

    if Confirm.ask(f"Switch to {other_mode} mode?", default=False):
        switch_mode(other_mode)
    else:
        console.print("[yellow]Switch cancelled[/yellow]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage: config.py <command> [args][/red]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        status()
    elif command == "switch":
        if len(sys.argv) < 3:
            console.print("[red]Usage: config.py switch <mode>[/red]")
            sys.exit(1)
        switch_mode(sys.argv[2])
    elif command == "switch-interactive":
        switch_interactive()
    elif command == "sync-profile":
        sync_profile()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        sys.exit(1)
