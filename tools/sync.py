#!/usr/bin/env python3
"""Sync config templates with personal configs"""
from pathlib import Path
import tomli
from rich.console import Console
from rich.table import Table

console = Console()

CONFIG_DIR = Path.home() / ".claude" / "configs"
# Auto-detect repo location (tools/ is one level down from repo root)
REPO_DIR = Path(__file__).parent.parent.resolve()


def compare_configs():
    """Compare template configs with user configs"""
    current_mode_file = CONFIG_DIR / "current_mode"
    if not current_mode_file.exists():
        console.print("[yellow]No mode configured[/yellow]")
        return

    mode = current_mode_file.read_text().strip()

    # Load template
    template_path = REPO_DIR / f"configs/{mode}.toml"
    with open(template_path, "rb") as f:
        template = tomli.load(f)

    # Load user config (if exists)
    user_env = CONFIG_DIR / f"{mode}.env"
    if not user_env.exists():
        console.print(f"[red]User config missing: {user_env}[/red]")
        return

    # Compare structure
    console.print(f"\n[bold]Comparing {mode} template with your config[/bold]\n")

    # Show version
    version_file = REPO_DIR / "VERSION"
    repo_version = version_file.read_text().strip() if version_file.exists() else "unknown"
    user_version_file = CONFIG_DIR / ".version"
    user_version = user_version_file.read_text().strip() if user_version_file.exists() else "unknown"

    console.print(f"Repo version: {repo_version}")
    console.print(f"Your version: {user_version}")

    if user_version != repo_version:
        console.print("\n[yellow]Updates available! Check CHANGELOG.md[/yellow]")
        changelog = REPO_DIR / "CHANGELOG.md"
        if changelog.exists():
            console.print("\nRecent changes:")
            # Show relevant changelog section
            content = changelog.read_text()
            # Simple extraction - could be improved
            console.print(content[:500])

    console.print(f"\n[green]Review template: {template_path}[/green]")
    console.print(f"[green]Your config: {user_env}[/green]")
    console.print("\nManually compare and update if needed")


if __name__ == "__main__":
    compare_configs()
