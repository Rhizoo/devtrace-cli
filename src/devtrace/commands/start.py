import typer
import subprocess
from datetime import datetime
from pathlib import Path
import toml
from rich.console import Console

# This makes "devtrace start <ticket>" work directly (no group)
app = typer.Typer(
    help="Start working on a Jira ticket",
    invoke_without_command=True,   # ← Important
    add_completion=False
)

console = Console()

@app.callback()
def start(
    ticket_id: str = typer.Argument(..., help="Jira ticket ID (e.g. DT-123)"),
):
    """Update local_config.toml:
       • active.ticket_id
       • active.started_at
       • active.branch (current git branch)"""

    ticket_id = ticket_id.upper().strip()

    if not ticket_id or "-" not in ticket_id:
        console.print("[red]Invalid ticket ID. Must be like DT-123[/]")
        raise typer.Exit(1)

    # Get current branch
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if not branch:
            branch = "main"
    except Exception:
        console.print("[yellow]Warning: Not in a git repo. Using 'main'[/]")
        branch = "main"

    # Timestamp exactly like your local_config.toml
    started_at = datetime.now().astimezone().isoformat()

    # Config path
    config_path = Path(".devtrace/configs/local/local_config.toml")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load or create config
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = toml.load(f)
    else:
        config = {}

    # Update [active] section only
    if "active" not in config:
        config["active"] = {}

    config["active"]["ticket_id"] = ticket_id
    config["active"]["started_at"] = started_at
    config["active"]["branch"] = branch

    # Save (preserves all other sections)
    with open(config_path, "w", encoding="utf-8") as f:
        toml.dump(config, f)

    console.print(f"[green]✓ Started ticket [bold]{ticket_id}[/][/]")
    console.print(f"   Branch   : {branch}")
    console.print(f"   Started  : {started_at}")