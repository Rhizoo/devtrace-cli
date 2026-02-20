import re
import tomllib
import typer
from pathlib import Path
from rich.console import Console
from typing import Optional

# This makes "devtrace format <file>" work directly (no double "format")
app = typer.Typer(
    help="Smart commit message formatter",
    invoke_without_command=True,   # ← This is the key
    add_completion=False
)

console = Console()

def load_rules(rules_path: Path):
    if not rules_path.exists():
        console.print(f"[red]Rules file not found: {rules_path}[/]")
        raise typer.Exit(1)
    with rules_path.open("rb") as f:
        return tomllib.load(f)

def load_local(local_path: Path):
    if not local_path.exists():
        return {"active": {}, "settings": {"formater": True}}
    with local_path.open("rb") as f:
        return tomllib.load(f)

def get_active_ticket(local_path: Path) -> Optional[str]:
    local = load_local(local_path)
    return local.get("active", {}).get("ticket_id")

@app.callback()
def format(
    msg_file: Path = typer.Argument(..., help="Commit message file (edited in-place)"),
    rules_path: Path = typer.Option(
        Path(".devtrace/configs/rules.toml"), "--rules-path"
    ),
    local_path: Path = typer.Option(
        Path(".devtrace/configs/local/local_config.toml"), "--local-path"
    ),
):
    """Smart formatter. Handles:
       • dt-14 bug fix
       • feat buttton fixed
       • completely raw message
       • broken formats"""
    if not msg_file.exists():
        console.print(f"[red]Message file not found: {msg_file}[/]")
        raise typer.Exit(1)

    raw = msg_file.read_text(encoding="utf-8").strip()
    if not raw:
        return

    rules = load_rules(rules_path)
    local = load_local(local_path)

    if not local.get("settings", {}).get("formater", True):
        console.print("[dim]Formatter disabled in local config[/]")
        return

    allowed_types = [t.upper() for t in rules.get("types", {}).get("allowed", ["FEAT", "FIX", "CHORE", "DOCS", "REFACTOR", "TEST"])]
    default_type = rules.get("commit", {}).get("default_type", "FEAT").upper()

    ticket_re = re.compile(r"^([A-Za-z]+-\d+)", re.IGNORECASE)
    type_re   = re.compile(r"^([A-Za-z]+)\b", re.IGNORECASE)

    # Case 1: Already perfect
    if re.match(r"^([A-Z]+-\d+)\s\|\s([A-Z]+)\s:\s(.+)$", raw):
        return

    # Case 2: Has ticket but no type → "dt-14 bug fix"
    m = ticket_re.match(raw)
    if m:
        ticket = m.group(1).upper()
        desc = raw[m.end():].strip(" |:")
        new_msg = f"{ticket} | {default_type} : {desc}"
        msg_file.write_text(new_msg + "\n", encoding="utf-8")
        console.print(f"[green]Added type → {new_msg}[/]")
        return

    # Case 3: Starts with type but no ticket → "feat buttton fixed"
    m = type_re.match(raw)
    if m:
        typ = m.group(1).upper()
        if typ in allowed_types:
            desc = raw[m.end():].strip(" |:")
            active = get_active_ticket(local_path)
            ticket = active.upper() if active else "NO-TICKET"
            new_msg = f"{ticket} | {typ} : {desc}"
            msg_file.write_text(new_msg + "\n", encoding="utf-8")
            console.print(f"[green]Added ticket → {new_msg}[/]")
            return

    # Case 4: Completely raw
    active = get_active_ticket(local_path)
    if active:
        new_msg = f"{active.upper()} | {default_type} : {raw.strip()}"
        msg_file.write_text(new_msg + "\n", encoding="utf-8")
        console.print(f"[green]Full format applied → {new_msg}[/]")
        return

    console.print("[yellow]No active ticket. Run `devtrace start <TKT>` first.[/]")