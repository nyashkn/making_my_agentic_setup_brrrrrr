#!/usr/bin/env python3
"""Installation script"""
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
# Auto-detect repo location (tools/ is one level down from repo root)
REPO_DIR = Path(__file__).parent.parent.resolve()


def install():
    """Run installation"""
    console.print("[bold]Installing Claude Code Configuration[/bold]\n")

    # Create config directory
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Copy personal template
    personal_template = REPO_DIR / "configs/personal.toml.example"
    personal_config = CONFIG_DIR / "personal.toml"

    if not personal_config.exists():
        personal_config.write_text(personal_template.read_text())
        console.print(f"[green]Created: {personal_config}[/green]")

    # Ask for default mode
    mode = Prompt.ask(
        "Choose default mode",
        choices=["anthropic", "bedrock"],
        default="anthropic"
    )

    current_mode_file = CONFIG_DIR / "current_mode"
    current_mode_file.write_text(mode)

    # Generate initial .env file for the chosen mode
    import sys
    sys.path.insert(0, str(REPO_DIR / "tools"))
    from config import load_config, apply_config

    console.print(f"[cyan]Generating {mode}.env configuration...[/cyan]")
    config = load_config(mode)
    apply_config(config)

    # Save version
    version_file = REPO_DIR / "VERSION"
    if version_file.exists():
        user_version_file = CONFIG_DIR / ".version"
        user_version_file.write_text(version_file.read_text())

    # Add to shell config
    zshrc = Path.home() / ".zshrc"
    source_line = f"source {REPO_DIR}/shell/zsh-functions.sh"

    if zshrc.exists():
        content = zshrc.read_text()
        if source_line not in content:
            with open(zshrc, "a") as f:
                f.write(f"\n# Claude Code Config (auto-detected location)\n{source_line}\n")
            console.print(f"[green]Added to {zshrc}[/green]")
            console.print(f"[yellow]Note: Shell functions sourced from {REPO_DIR}[/yellow]")

    # Add claude-switch alias for convenience
    alias_line = f"alias claude-switch='make -C {REPO_DIR} switch'"
    if zshrc.exists():
        content = zshrc.read_text()
        if "alias claude-switch=" not in content:
            with open(zshrc, "a") as f:
                f.write(f"\n# Claude mode switching alias (switch from anywhere)\n{alias_line}\n")
            console.print(f"[green]Added claude-switch alias to {zshrc}[/green]")

    console.print("\n[bold green]Installation complete![/bold green]")
    console.print(f"\n1. Edit: {personal_config}")
    console.print("2. Run: source ~/.zshrc")
    console.print("3. Run: make status")
    console.print("\nTip: Use 'claude-switch' from anywhere to switch modes")


if __name__ == "__main__":
    install()
