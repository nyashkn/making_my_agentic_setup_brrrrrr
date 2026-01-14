#!/usr/bin/env python3
"""Configuration validation"""
from pathlib import Path
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
REPO_DIR = Path(__file__).parent.parent.resolve()


def validate():
    """Validate current configuration"""
    console.print("[bold]Validating configuration...[/bold]\n")

    # Check if configs exist
    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[red]No mode configured. Run 'task install' first.[/red]")
        return False

    mode = current_mode_file.read_text().strip()
    env_file = CONFIG_DIR / f"{mode}.env"

    if not env_file.exists():
        console.print(f"[red]Config file missing: {env_file}[/red]")
        console.print(f"Run: task switch -- {mode}")
        return False

    console.print(f"[green]Mode: {mode}[/green]")
    console.print(f"[green]Config file: {env_file}[/green]")
    console.print("\n[green]Configuration looks good![/green]")
    return True


if __name__ == "__main__":
    import sys
    result = validate()
    sys.exit(0 if result else 1)
