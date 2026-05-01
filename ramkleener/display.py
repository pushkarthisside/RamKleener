# ============================================================
#  display.py — RamKleener Terminal UI
#  v1.3 Meta: Optimized for performance and terminal aesthetic.
#  Uses custom block-bars and simplified summary logic.
# ============================================================

from rich.console import Console
from rich.table import Table
from rich.markup import escape  # CRITICAL: Prevents names with [brackets] from crashing UI
from rich import box

console = Console()

def render_ram_bar(ram_stats):
    """
    Renders a custom block-style RAM usage bar [████░░░].
    Colors: Green < 60%, Yellow 60-80%, Red > 80%.
    """
    percent   = ram_stats["percent_used"]
    used_gb   = ram_stats["used_mb"]  / 1024
    total_gb  = ram_stats["total_mb"] / 1024

    if percent < 60:
        color = "green"
    elif percent < 80:
        color = "yellow"
    else:
        color = "red"

    # Custom ASCII Bar Logic
    bar_width = 30
    filled = int(percent / 100 * bar_width)
    empty  = bar_width - filled
    bar    = "█" * filled + "░" * empty

    console.print()
    console.print(
        f"  RAM  [[{color}]{bar}[/{color}]]  "
        f"{percent:.1f}%   {used_gb:.1f} / {total_gb:.1f} GB"
    )
    console.print()


def render_scan_table(flagged):
    """Renders a standard table for the 'Scan' mode."""
    if not flagged:
        console.print("  [green]✓ No bloat processes found above threshold.[/green]\n")
        return

    table = Table(
        title="Flagged Processes",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold white",
        border_style="bright_black",
    )

    table.add_column("#",      style="dim",          width=4,  justify="right")
    table.add_column("PID",    style="cyan",          width=8,  justify="right")
    table.add_column("Name",   style="white",         width=30, justify="left")
    table.add_column("RAM",    style="yellow",        width=12, justify="right")

    for i, proc in enumerate(flagged, start=1):
        table.add_row(
            str(i),
            str(proc["pid"]),
            escape(proc["name"]),
            f"{proc['ram_mb']:.1f} MB"
        )

    console.print(table)
    console.print()


def render_grouped_table(groups):
    """Renders aggregated table for 'Kill One by One' mode."""
    if not groups:
        console.print("  [green]✓ No bloat processes found.[/green]\n")
        return

    table = Table(
        title="Flagged Processes (Grouped)",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold white",
        border_style="bright_black",
    )

    table.add_column("#",         style="dim",          width=4,  justify="right")
    table.add_column("Name",      style="white",         width=28, justify="left")
    table.add_column("Instances", style="cyan",          width=10, justify="right")
    table.add_column("Total RAM", style="yellow",        width=12, justify="right")

    for i, group in enumerate(groups, start=1):
        table.add_row(
            str(i),
            escape(group["name"]),
            str(group["count"]),
            f"{group['ram_mb']:.1f} MB"
        )

    console.print(table)
    console.print()


def render_kill_summary(results, ram_after=None):
    """
    Renders summary with a borderless table.
    Only displays the 'After' RAM status for a cleaner look.
    """
    if not results:
        console.print("  [dim]Nothing to summarize.[/dim]\n")
        return

    killed  = [r for r in results if r["success"]]
    skipped = [r for r in results if not r["success"]]
    freed   = sum(r["ram_mb"] for r in killed)

    summary_table = Table(box=None, show_header=False, pad_edge=False)
    summary_table.add_column("Status", width=12)
    summary_table.add_column("Name",   width=30)
    summary_table.add_column("Impact", width=15)

    for r in results:
        status = "[green]✓ Killed[/green]" if r["success"] else "[red]✗ Skipped[/red]"
        impact = f"[yellow]{r['ram_mb']:.1f} MB[/yellow]" if r["success"] else f"[dim]{r.get('reason', '')}[/dim]"
        summary_table.add_row(status, escape(r['name']), impact)

    console.print("\n  [bold]Cleaning Results:[/bold]")
    console.print(summary_table)

    console.print(
        f"\n  [bold]Final Summary:[/bold] "
        f"[green]{len(killed)} killed[/green], "
        f"[dim]{len(skipped)} skipped[/dim], "
        f"~[yellow]{freed:.0f} MB freed[/yellow]"
    )

    if ram_after:
        console.print("  [dim]RAM after cleaning:[/dim]")
        render_ram_bar(ram_after)


def render_help():
    """Prints the Help screen."""
    console.print()
    console.rule("[bold cyan]RamKleener — How It Works[/bold cyan]")
    console.print("""
  RamKleener scans your running processes against two tiers:

  [bold green]PROTECTED[/bold green]    — System-critical processes. Locked forever.
  [bold yellow]SAFE_TO_KILL[/bold yellow] — Known background bloat. These get terminated.

  Unknown processes are [bold]always skipped[/bold] — Safety by default.

  [bold cyan]Menu Options[/bold cyan]
  ─────────────────────────────────────────────────
  1. Scan             Show all running bloat processes.
  2. Kill all         Kill everything found in one shot.
  3. Kill one by one  Step through each group — [b]y[/b]=kill, [b]n[/b]=skip, [b]q[/b]=quit early.
  4. Help             This screen.
  5. About            Version and author info.
  0. Exit             Quit RamKleener.
    """)
    console.print()


def render_about():
    """Prints the About screen."""
    console.print()
    console.rule("[bold cyan]About RamKleener[/bold cyan]")
    console.print("""
  [bold white]RamKleener[/bold white] v1.3
  A safe, minimal Python CLI tool for killing memory-bloating background processes.

  [bold cyan]Author[/bold cyan]    Pushkar :3
  [bold cyan]GitHub[/bold cyan]    https://github.com/pushkarthisside/RamKleener
  [bold cyan]Stack[/bold cyan]     Python 3 · psutil · rich
    """)
    console.print()