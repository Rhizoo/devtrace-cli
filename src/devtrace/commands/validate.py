import typer
import re
import tomllib
from pathlib import Path
from rich.console import Console

# Correct relative import (same commands/ folder)
from .format import format

console = Console()

app = typer.Typer(help="DevTrace validator")

def load_rules(rules_path: Path):
    if not rules_path.exists():
        console.print(f"[red]Rules file not found: {rules_path}[/]")
        raise typer.Exit(1)
    with rules_path.open("rb") as f:
        return tomllib.load(f)

@app.command()
def commit(
    msg_file: Path = typer.Argument(..., help="Commit message file"),
    rules_path: Path = typer.Option(
        Path(".devtrace/configs/rules.toml"),
        "--rules-path",
    ),
    local_path: Path = typer.Option(
        Path(".devtrace/configs/local/local_config.toml"),
        "--local-path",
    ),
    no_format: bool = typer.Option(
        False,
        "--no-format",
        help="Skip auto-formatting (strict enforcement only)",
    ),
):
    """Validate commit message. Auto-formats unless --no-format."""
    if not msg_file.exists():
        console.print(f"[red]Message file not found: {msg_file}[/]")
        raise typer.Exit(1)

    if not no_format:
        format(msg_file, rules_path=rules_path, local_path=local_path)
        commit_msg = msg_file.read_text(encoding="utf-8").strip().splitlines()[0]
    else:
        commit_msg = msg_file.read_text(encoding="utf-8").strip().splitlines()[0]

    rules = load_rules(rules_path)
    pattern = rules.get("commit", {}).get(
        "pattern", r"^([A-Z]+-\d+)\s\|\s([A-Z]+)\s:\s(.+)$"
    )

    if not re.match(pattern, commit_msg):
        console.print("[red]Invalid commit format![/]")
        console.print(f"Expected: TICKET | TYPE : description")
        console.print(f"Got:      {commit_msg}")
        raise typer.Exit(1)

    m = re.match(r"^([A-Z]+-\d+)\s\|\s([A-Z]+)\s:\s(.+)$", commit_msg)
    if not m:
        console.print("[red]Could not parse final message[/]")
        raise typer.Exit(1)

    ticket, commit_type, _ = m.groups()

    allowed_types = [t.upper() for t in rules.get("types", {}).get("allowed", [])]
    if commit_type not in allowed_types:
        console.print(f"[red]Unknown type: {commit_type}[/]")
        console.print(f"Allowed: {', '.join(allowed_types)}")
        raise typer.Exit(1)

    console.print("[green]Commit message OK[/]")