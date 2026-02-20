import typer
import subprocess
import toml
from pathlib import Path
from rich.console import Console

app = typer.Typer(
    invoke_without_command=True,
    help="Initialize devtrace project or specific components"
)
console = Console()

# Easy to extend: add new hooks here
HOOKS = {
    "prepare-commit-msg": """#!/bin/sh
# Smart formatter (never blocks)
devtrace format "$1"
exit 0
""",

    "commit-msg": """#!/bin/sh
# Strict validation
devtrace validate commit "$1" --no-format
if [ $? -ne 0 ]; then
    exit 1
fi
"""
}


@app.callback()
def main_callback(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files/folders")
):
    if ctx.invoked_subcommand is not None:
        return

    base_path = Path(".devtrace").resolve()

    if base_path.exists() and not force:
        console.print("[yellow]Directory already exists. Use --force to overwrite.[/]")
        raise typer.Exit(1)

    console.print(f"[bold green]Initializing DevTrace in {base_path}[/]")

    # Create folders
    for folder in [base_path / "configs", base_path / "logs", base_path / "hooks"]:
        folder.mkdir(parents=True, exist_ok=True)
        console.print(f"[dim]Created: {folder.relative_to(base_path)}[/]")

    # Create subfolders
    for sub in [base_path / "configs" / d for d in ["local", "global", "jira", "git"]]:
        sub.mkdir(exist_ok=True)
        console.print(f"[dim]Created sub: {sub.relative_to(base_path)}[/]")

    # Create config files
    configs = {
        base_path / "configs" / "rules.toml": {
            "commit": {"pattern": "^[A-Z]+-\\d+\\s\\|\\s[A-Z]+\\s:\\s.+$", "default_type":"FEAT", "strict": True},
            "ticket": {"pattern": "^[A-Z]+-\\d+$", "uppercase": True},
            "types": {"allowed": ["FEAT", "FIX", "INIT", "DOCS", "REFACTOR", "TEST", "CHORE"]},
            "severity": {"invalid_format": "error", "unknown_type": "error", "missing_ticket": "error"}
        },
        base_path / "configs" / "global" / "global_config.toml": {
            "commit": {"pattern": "^[A-Z]+-\\d+\\s\\|\\s[A-Z]+\\s:\\s.+$", "strict": True},
            "ticket": {"pattern": "^[A-Z]+-\\d+$", "uppercase": True},
            "types": {"allowed": ["FEAT", "FIX", "INIT", "DOCS", "REFACTOR", "TEST", "CHORE"]},
            "severity": {"invalid_format": "error", "unknown_type": "error", "missing_ticket": "error"}
        },
        base_path / "configs" / "local" / "local_config.toml": {
            "active": {"ticket_id": "DT-1", "started_at": "2026-02-19T20:15:00+05:30", "branch":"main"},
            "types": {"allowed": ["FEAT", "FIX", "INIT", "DOCS", "REFACTOR", "TEST", "CHORE"]},
            "settings" : {"formater" : True, }
        },
    }
    for file_path, content in configs.items():
        if file_path.exists() and not force:
            console.print(f"[yellow]Skipping existing: {file_path.relative_to(base_path)}[/]")
            continue
        with file_path.open("w", encoding="utf-8") as f:
            toml.dump(content, f)
        console.print(f"[dim]Created config: {file_path.relative_to(base_path)}[/]")

    # Create hooks
    for name, content in HOOKS.items():
        hook_path = base_path / "hooks" / name
        hook_path.write_text(content, encoding="utf-8")
        hook_path.chmod(0o755)
        console.print(f"[green]✓ Created hook: {name}[/]")

    # Add local config to .gitignore
    gitignore_path = Path(".gitignore")
    entry = ".devtrace/configs/local/"
    if gitignore_path.exists():
        if entry.strip() not in gitignore_path.read_text(encoding="utf-8"):
            with gitignore_path.open("a", encoding="utf-8") as f:
                f.write(f"\n# DevTrace - per-developer local config\n{entry}\n")
            console.print("[green]✓ Added local config to .gitignore[/]")
    else:
        gitignore_path.write_text(f"# DevTrace\n{entry}\n", encoding="utf-8")
        console.print("[green]✓ Created .gitignore with local config entry[/]")

    # Activate git hooks if inside repo
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=base_path.parent, check=True, capture_output=True)
        subprocess.run(["git", "config", "core.hooksPath", ".devtrace/hooks"], cwd=base_path.parent, check=True)
        console.print("[bold green]✓ Git hooks activated[/]")
    except subprocess.CalledProcessError:
        console.print("[yellow]Not inside git repo yet[/]")
    except FileNotFoundError:
        console.print("[red]Git not found in PATH[/]")

    console.print("[bold green]DevTrace initialization complete![/]")


# Subcommands
@app.command()
def hooks():
    """Re-apply hooks"""
    try:
        subprocess.run(["git", "config", "core.hooksPath", ".devtrace/hooks"], check=True)
        console.print("[bold green]Git hooks re-activated[/]")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/]")


@app.command()
def jira(config_path: str = typer.Option("configs/jira.toml", help="Path to Jira config")):
    console.print(f"[yellow]Jira setup at {config_path}[/]")


@app.command()
def git(hook_dir: str = typer.Option("hooks", help="Hook directory")):
    console.print(f"[yellow]Git setup in {hook_dir}[/]")


if __name__ == "__main__":
    app()