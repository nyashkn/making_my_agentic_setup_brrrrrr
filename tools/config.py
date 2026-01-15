#!/usr/bin/env python3
"""Claude Code configuration management"""
import sys
from pathlib import Path
from typing import Dict, Any
import tomli
import tomli_w
from rich.console import Console
from rich.table import Table

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
# Auto-detect repo location (tools/ is one level down from repo root)
REPO_DIR = Path(__file__).parent.parent.resolve()


def load_config(mode: str) -> Dict[str, Any]:
    """Load mode config with personal overrides"""
    # Load base config
    base_path = REPO_DIR / f"configs/{mode}.toml"
    with open(base_path, "rb") as f:
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


def apply_config(config: Dict[str, Any], dry_run: bool = False) -> None:
    """Apply config to environment"""
    mode = config["mode"]
    models = config["models"]
    performance = config.get("performance", {})
    optional = config.get("optional", {})

    exports = []
    exports.append(f"export CLAUDE_CODE_USE_BEDROCK={'1' if mode['use_bedrock'] else '0'}")
    exports.append(f"export ANTHROPIC_MODEL='{models['primary']}'")
    exports.append(f"export ANTHROPIC_DEFAULT_HAIKU_MODEL='{models['haiku']}'")
    exports.append(f"export ANTHROPIC_DEFAULT_SONNET_MODEL='{models['sonnet']}'")
    exports.append(f"export ANTHROPIC_DEFAULT_OPUS_MODEL='{models['opus']}'")
    exports.append(f"export CLAUDE_CODE_SUBAGENT_MODEL='{models['subagent']}'")

    if mode["use_bedrock"] and "aws" in config:
        exports.append(f"export AWS_REGION='{config['aws']['region']}'")
        exports.append(f"export AWS_PROFILE='{config['aws']['profile']}'")

    if performance.get("max_thinking_tokens"):
        exports.append(f"export MAX_THINKING_TOKENS={performance['max_thinking_tokens']}")

    if performance.get("disable_prompt_caching"):
        exports.append("export DISABLE_PROMPT_CACHING=1")

    if optional.get("disable_telemetry"):
        exports.append("export DISABLE_TELEMETRY=1")

    if optional.get("playwright_headless") is False:
        exports.append("export PLAYWRIGHT_HEADLESS=false")

    script = "\n".join(exports)

    if dry_run:
        console.print(script)
    else:
        out_file = CONFIG_DIR / f"{mode['name']}.env"
        out_file.write_text(script)
        console.print(f"[green]Applied {mode['name']} config to {out_file}[/green]")


def status():
    """Show current config status"""
    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[red]No mode configured[/red]")
        return

    mode = current_mode_file.read_text().strip()
    config = load_config(mode)

    table = Table(title="Claude Code Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Mode", mode)
    table.add_row("Bedrock", str(config["mode"]["use_bedrock"]))
    table.add_row("Primary Model", config["models"]["primary"])
    table.add_row("Subagent Model", config["models"]["subagent"])

    if config["mode"]["use_bedrock"]:
        table.add_row("AWS Region", config.get("aws", {}).get("region", "N/A"))
        table.add_row("AWS Profile", config.get("aws", {}).get("profile", "N/A"))

    console.print(table)


def switch_mode(mode: str):
    """Switch to a different mode"""
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


def switch_interactive():
    """Interactive mode switching - prompts to switch to other mode"""
    from rich.prompt import Confirm

    current_mode_file = CONFIG_DIR / "current_mode"

    # Check if mode is configured
    if not current_mode_file.exists():
        console.print("[yellow]No mode configured. Run: task install[/yellow]")
        sys.exit(1)

    current_mode = current_mode_file.read_text().strip()

    # Determine the other mode
    other_mode = "bedrock" if current_mode == "anthropic" else "anthropic"

    # Show current status
    console.print(f"\n[cyan]Current mode:[/cyan] {current_mode}")
    console.print(f"[cyan]Switch to:[/cyan] {other_mode}\n")

    # Confirm switch
    if Confirm.ask(f"Switch to {other_mode} mode?", default=False):
        switch_mode(other_mode)
    else:
        console.print("[yellow]Switch cancelled[/yellow]")


if __name__ == "__main__":
    import sys

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
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        sys.exit(1)
