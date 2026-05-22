# ============================================================
#  display.py — RamKleener v2.0
#  All terminal UI — header, RAM bar, scan progress,
#  process table, and summary panels.
# ============================================================

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.markup import escape
import psutil

console = Console()


# ── RAM Bar ──────────────────────────────────────────────────

def get_ram_stats() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 1),
        "used_gb":  round(mem.used  / (1024 ** 3), 1),
        "free_gb":  round(mem.available / (1024 ** 3), 1),
        "pct":      mem.percent
    }


def show_ram_bar() -> None:
    r = get_ram_stats()
    pct = r["pct"]

    if pct >= 85:
        color = "red"
    elif pct >= 65:
        color = "yellow"
    else:
        color = "green"

    bar_len = 30
    filled  = int(pct / 100 * bar_len)
    empty   = bar_len - filled
    bar     = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"

    line = Text()
    line.append("  RAM  ")
    console.print(
        f"  RAM  [{bar}]  [{color}]{pct}%[/{color}]"
        f"   [dim]{r['used_gb']} / {r['total_gb']} GB[/dim]"
    )


# ── Header ───────────────────────────────────────────────────

def show_header(is_admin: bool) -> None:
    console.clear()
    console.print()
    console.print(Panel(
        "[bold cyan]RamKleener v2.0[/bold cyan]  [dim]by Pushkar[/dim]",
        box=box.DOUBLE,
        expand=False,
        padding=(0, 4)
    ))

    if not is_admin:
        console.print(
            "  [yellow][!] Not running as Admin — some kills may fail.[/yellow]"
        )

    show_ram_bar()
    console.print()


# ── Scan Progress Bar ─────────────────────────────────────────

def run_scan_with_progress(config: dict) -> tuple[list[dict], dict]:
    """
    Runs the scan with a live progress bar.
    Imports scanner here to avoid circular imports.
    """
    from ramkleener.scanner import scan_processes

    with Progress(
        TextColumn("  [cyan]Scanning...[/cyan]"),
        BarColumn(bar_width=30, complete_style="cyan", finished_style="green"),
        TaskProgressColumn(),
        transient=True,       # clears the bar after scan completes
        console=console
    ) as progress:

        task = progress.add_task("scan", total=100)

        # Pulse progress while scanning (scan is synchronous)
        # We simulate progress in thirds — start, mid, done
        progress.update(task, advance=20)
        bloat_list, metadata = scan_processes(config)
        progress.update(task, completed=100)

    return bloat_list, metadata


# ── Process Table ─────────────────────────────────────────────

def show_bloat_table(bloat_list: list[dict], metadata: dict) -> None:
    console.print()

    # Metadata line above table
    console.print(
        f"  [dim]Scanned [white]{metadata['total_scanned']}[/white] processes"
        f" — threshold [white]{metadata['threshold_used']} MB[/white][/dim]"
    )
    console.print()

    if not bloat_list:
        console.print(
            Panel(
                "[green]No bloat processes found above threshold.[/green]",
                box=box.ROUNDED,
                padding=(0, 2)
            )
        )
        console.print()
        return

    # Group by name
    grouped: dict[str, dict] = {}
    for proc in bloat_list:
        name = proc["name"]
        if name not in grouped:
            grouped[name] = {"name": name, "instances": 0, "total_mb": 0.0}
        grouped[name]["instances"] += 1
        grouped[name]["total_mb"]  += proc["mem_mb"]

    rows = sorted(grouped.values(), key=lambda x: x["total_mb"], reverse=True)

    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="dim",
        padding=(0, 1),
        expand=False
    )

    table.add_column("Process",   style="white",    min_width=22)
    table.add_column("Instances", style="dim",       justify="right", min_width=9)
    table.add_column("Memory",    justify="right",   min_width=10)

    for row in rows:
        mb = round(row["total_mb"], 1)

        if mb >= 200:
            mem_str = f"[red]{mb} MB[/red]"
        elif mb >= 100:
            mem_str = f"[yellow]{mb} MB[/yellow]"
        else:
            mem_str = f"{mb} MB"

        # FIX: Escape the process name to prevent rich markup crashes
        safe_name = escape(row["name"])

        table.add_row(
            safe_name,
            f"x{row['instances']}",
            mem_str
        )

    console.print(table)

    # Total line
    total_mb = round(metadata["total_bloat_mem"], 1)
    total_color = "red" if total_mb >= 500 else "yellow" if total_mb >= 200 else "white"
    console.print(
        f"  [dim]Total bloat RAM:[/dim]"
        f"  [{total_color}]{total_mb} MB[/{total_color}]"
        f"  [dim]across {len(bloat_list)} processes[/dim]"
    )
    console.print()


# ── Clean Summary ─────────────────────────────────────────────

def show_clean_summary(
    killed: int,
    already_gone: int,
    denied: int,
    other_fail: int,
    est_impact_mb: float,
    temp_deleted: int,
    temp_mb: float
) -> None:

    lines = []
    lines.append(f"[white]Killed:[/white]              [green]{killed}[/green] process(es)")
    lines.append(f"[white]Est. memory impact:[/white]  [cyan]{round(est_impact_mb, 1)} MB[/cyan]")
    lines.append(f"[white]Temp files removed:[/white]  [cyan]{temp_deleted} files / {temp_mb} MB[/cyan]")

    if already_gone:
        lines.append(f"[white]Already closed:[/white]      [dim]{already_gone}[/dim]")
    if denied:
        lines.append(f"[white]Access denied:[/white]       [red]{denied} (try running as Admin)[/red]")
    if other_fail:
        lines.append(f"[white]Other failures:[/white]      [dim]{other_fail}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title="[bold]Summary[/bold]",
        box=box.ROUNDED,
        padding=(0, 2)
    ))
    console.print()


# ── Menu ──────────────────────────────────────────────────────

def show_menu() -> None:
    console.print(Panel(
        "[white]1.[/white]  Scan processes\n"
        "[white]2.[/white]  Clean RAM  [dim](kill bloat + clear temp)[/dim]\n"
        "[white]3.[/white]  Full clean [dim](scan + kill + show RAM after)[/dim]\n"
        "[white]4.[/white]  Help\n"
        "[white]5.[/white]  About\n"
        "[dim]0.  Exit[/dim]",
        box=box.SIMPLE,
        padding=(0, 2)
    ))


def show_help() -> None:
    console.print(Panel(
        "[dim]RamKleener scans for memory-bloating processes\n"
        "and kills them safely using a 3-tier protection model.[/dim]\n\n"
        "[red]Tier 1 — NEVER_KILL_CORE   :[/red] locked forever (OS critical)\n"
        "[yellow]Tier 2 — NEVER_KILL_DEFAULT:[/yellow] protected by default\n"
        "[green]Tier 3 — SAFE_TO_KILL      :[/green] known bloat, killed if found\n\n"
        "[dim]Run as Admin for best results.[/dim]",
        title="Help",
        box=box.ROUNDED,
        padding=(0, 2)
    ))
    console.print()


def show_about() -> None:
    console.print(Panel(
        "[white]RamKleener v2.0[/white]\n"
        "[dim]Built by Pushkar\n"
        "Phase 1: PowerShell  |  Phase 2: Python\n"
        "github.com/pushkarthisside/RamKleener[/dim]",
        box=box.ROUNDED,
        padding=(0, 2)
    ))
    console.print()
