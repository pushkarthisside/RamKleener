# ============================================================
#  display.py — RamKleener Terminal UI (v2.2 Production UI)
# ============================================================

from rich.console import Console
from rich.table import Table
from rich.markup import escape  # Prevents app names with [brackets] from breaking Rich syntax
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

    # ASCII Bar Logic
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
    """Renders a standard table for 'Scan' mode."""
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

    table.add_column("#",      style="dim",      width=4,  justify="right")
    table.add_column("PID",    style="cyan",     width=8,  justify="right")
    table.add_column("Name",   style="white",    width=30, justify="left")
    table.add_column("RAM",    style="yellow",   width=12, justify="right")

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
    """Renders borderless table post-cleaning summary."""
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


def render_discovery_table(flagged, mode="clean"):
    """
    Renders the configuration table with context-aware colors.
    mode="clean": Killable=Green, Neutral=Yellow, Protected=Red
    mode="safe": Protected=Green, Neutral=Yellow, Killable=Red
    """
    if not flagged:
        return

    title = "Available Apps for Clean List" if mode == "clean" else "Available Apps for Safe List"
    
    table = Table(
        title=title,
        box=box.ROUNDED,
        header_style="bold white",
        border_style="bright_black",
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("App Name", width=25)
    table.add_column("RAM", style="dim", width=10, justify="right")
    table.add_column("Current Status", width=15)

    for i, p in enumerate(flagged, start=1):
        tier = p["tier"]
        name = escape(p["name"])
        ram = f"{p['ram_mb']:.1f} MB"

        if mode == "clean":
            if tier == "killable":
                color, status = "green", "✓ Clean Target"
            elif tier == "protected":
                color, status = "red", "🔒 Protected"
            else:
                color, status = "yellow", "❓ Neutral"
                
        elif mode == "safe":
            if tier == "protected":
                color, status = "green", "✓ Safe/Locked"
            elif tier == "killable":
                color, status = "red", "⚠️ Kill Target"
            else:
                color, status = "yellow", "❓ Neutral"

        table.add_row(str(i), f"[{color}]{name}[/{color}]", ram, f"[{color}]{status}[/{color}]")

    console.print(table)
    console.print()


def render_about():
    """Prints the About screen with cohesive color design."""
    console.print()
    console.rule("[bold white]About RamKleener[/bold white]") # Cohesive white border
    console.print("""
  [bold white]RamKleener[/bold white] v1.3
  A safe, minimal Python CLI tool for killing memory-bloating background processes.

  [bold white]Author:[/bold white]     [green]Pushkar :3[/green]
  [bold white]GitHub:[/bold white]     [white]https://github.com/pushkarthisside/RamKleener[/white]
  [bold white]Stack:[/bold white]      [yellow]Python 3 · psutil · rich[/yellow]
    """)
    console.print()


def render_help():
    """Prints the extensive Help screen with expanded, menu-grouped color code breakdowns."""
    console.print()
    console.rule("[bold white]RamKleener — Help & Documentation[/bold white]")
    console.print("""
  [bold white]Menu Options[/bold white]
  ─────────────────────────────────────────────────
  1. Scan             Show all active bloat apps above your RAM threshold.
  2. Kill all         Kill everything found in the scan instantly.
  3. Kill one by one  Step through groups one by one (y=kill, n=skip, q=quit).
  4. Customize Lists  Add/Remove custom apps from your Safe or Clean lists.

  [bold white]Understanding the Colors (By Menu)[/bold white]
  ─────────────────────────────────────────────────
  When you customize your lists, RamKleener color-codes apps so you instantly know
  their status. The meaning dynamically changes depending on the menu you are in.

  [bold underline white]Option 1 — Add / Remove Clean Apps[/bold underline white]

  • [bold green]✓ Clean Target[/bold green] [dim](Green)[/dim]
    This app is on your personal Kill List. During a scan, it will be flagged
    for termination if it exceeds your set RAM size limit.

  • [bold red]🔒 Protected[/bold red] [dim](Red)[/dim]
    Strict safety warning. This app is a critical OS process or manually locked
    in the Safe Menu. You are blocked from adding it to the Clean List.

  [bold underline white]Option 2 — Add / Remove Safe Apps[/bold underline white]

  • [bold green]✓ Safe / Locked[/bold green] [dim](Green)[/dim]
    This app is whitelisted on your Protected List. It is immune to RamKleener
    and will never be flagged, regardless of RAM usage.

  • [bold red]⚠ Kill Target[/bold red] [dim](Red)[/dim]
    Direct alert — this app is currently on your Kill List. Add it to the Safe
    List immediately if you want it protected. Safe always overrides Kill.

  [bold underline white]Neutral — Both Menus[/bold underline white]

  • [bold yellow]❓ Neutral[/bold yellow] [dim](Yellow)[/dim]
    No rules attached. RamKleener ignores this app entirely. You can push it
    to the Clean List to manage its RAM, or lock it in the Safe List.

  [bold white]The Golden Rule[/bold white]
  ─────────────────────────────────────────────────
  [bold green]PROTECTED[/bold green] rules over everything. If an app is on both lists or hardcoded
  as a critical OS process, it will [bold]never[/bold] be killed. Safety always wins.
    """)
    console.print()