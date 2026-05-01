# ============================================================
#  cli.py — RamKleener Entry Point & Menu Loop
#  v1.3 Meta: Final logic integration.
#  Ties all modules together and manages the user flow.
# ============================================================

from ramkleener.config import load_config
from ramkleener.scanner import scan_processes, get_system_ram
from ramkleener.cleaner import kill_all, kill_selective, group_by_name
from ramkleener.display import (
    console,
    render_ram_bar,
    render_scan_table,
    render_grouped_table,
    render_kill_summary,
    render_help,
    render_about,
)

MENU = """
  ┌─────────────────────────────┐
  │      R A M K L E E N E R    │
  ├─────────────────────────────┤
  │  1. Scan                    │
  │  2. Kill all                │
  │  3. Kill one by one         │
  │  4. Help                    │
  │  5. About                   │
  │  0. Exit                    │
  └─────────────────────────────┘
"""

def _require_scan(config):
    """
    Standardizes the Scan-and-Show flow.
    Returns (flagged, ram_stats) for use in before/after summaries.
    """
    ram_stats = get_system_ram()
    render_ram_bar(ram_stats)

    flagged = scan_processes(config)
    render_scan_table(flagged)

    return flagged, ram_stats


def _pause():
    """Prevents the menu from immediately clearing/scrolling results."""
    console.print("\n  [dim]Press Enter to return to menu...[/dim]")
    input()


def handle_scan(config):
    """Option 1: Scan and display only."""
    _require_scan(config)
    _pause()


def handle_kill_all(config):
    """Option 2: Scan then kill all with before/after RAM stats."""
    flagged, ram_before = _require_scan(config)

    if not flagged:
        _pause()
        return

    # Trigger the bulk kill engine
    results = kill_all(flagged)

    if results:
        ram_after = get_system_ram()
        render_kill_summary(results, ram_before=ram_before, ram_after=ram_after)
        _pause()


def handle_kill_selective(config):
    """Option 3: Grouped scan and step-through killing."""
    flagged, ram_before = _require_scan(config)

    if not flagged:
        _pause()
        return

    # Show the user what they are about to step through
    groups = group_by_name(flagged)
    render_grouped_table(groups)

    # Trigger the interactive kill engine
    # kill_selective returns (results, groups)
    results, _ = kill_selective(flagged)

    if results:
        ram_after = get_system_ram()
        render_kill_summary(results, ram_before=ram_before, ram_after=ram_after)
        _pause()


def main():
    """
    Main entry point. Loads config once per loop to allow
    live edits to config.json without restarting the tool.
    """
    console.print("\n  [bold cyan]RamKleener[/bold cyan] — v1.3 starting up...\n")

    while True:
        # LIVE RELOAD: Picks up changes to config.json immediately
        config = load_config()

        console.print(MENU, style="cyan")
        console.print("  Choice: ", end="", style="bold white")

        try:
            choice = input().strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n  [dim]Interrupted. Exiting.[/dim]\n")
            break

        if choice == "1":
            handle_scan(config)

        elif choice == "2":
            handle_kill_all(config)

        elif choice == "3":
            handle_kill_selective(config)

        elif choice == "4":
            render_help()
            _pause()

        elif choice == "5":
            render_about()
            _pause()

        elif choice == "0":
            console.print("\n  [dim]Bye.[/dim]\n")
            break

        else:
            console.print("\n  [red]Invalid choice.[/red] Enter 0–5.\n")


if __name__ == "__main__":
    main()