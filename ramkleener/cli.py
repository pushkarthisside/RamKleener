# ============================================================
#  cli.py — RamKleener Entry Point & Menu Loop (v2.2 Friendly UX)
# ============================================================

from ramkleener.config import load_config, save_config
from ramkleener.scanner import scan_processes, get_system_ram, scan_discovery_processes
from ramkleener.cleaner import kill_all, kill_selective, group_by_name
from ramkleener.display import (
    console,
    render_ram_bar,
    render_scan_table,
    render_grouped_table,
    render_kill_summary,
    render_help,
    render_about,
    render_discovery_table,
)

MENU = """
  ┌─────────────────────────────┐
  │      R A M K L E E N E R    │
  ├─────────────────────────────┤
  │  1. Scan                    │
  │  2. Kill all                │
  │  3. Kill one by one         │
  │  4. Customize Lists         │
  │  5. Help                    │
  │  6. About                   │
  │  0. Exit                    │
  └─────────────────────────────┘
"""

CUSTOMIZE_MENU = """
  ┌─────────────────────────────┐
  │      C U S T O M I Z E      │
  ├─────────────────────────────┤
  │  1. Add/Remove Clean Apps   │
  │  2. Add/Remove Safe Apps    │
  │  3. Adjust RAM Size Limit   │
  │  0. Back to Main Menu       │
  └─────────────────────────────┘
"""


def _require_scan(config):
    ram_stats = get_system_ram()
    render_ram_bar(ram_stats)

    flagged = scan_processes(config)
    render_scan_table(flagged)

    return flagged, ram_stats


def _pause():
    console.print("\n  [dim]Press Enter to continue...[/dim]")
    input()


def handle_scan(config):
    _require_scan(config)
    _pause()


def handle_kill_all(config):
    flagged, _ = _require_scan(config)
    if not flagged:
        _pause()
        return

    results = kill_all(flagged)
    if results:
        ram_after = get_system_ram()
        render_kill_summary(results, ram_after=ram_after)
        _pause()


def handle_kill_selective(config):
    flagged, _ = _require_scan(config)
    if not flagged:
        _pause()
        return

    # Compute groups once
    groups = group_by_name(flagged)
    render_grouped_table(groups)

    # Pass pre-computed groups down, avoiding double loops
    results = kill_selective(groups)

    if results:
        ram_after = get_system_ram()
        render_kill_summary(results, ram_after=ram_after)
        _pause()


def handle_customize():
    """Handles the simplified configuration menu with discovery scanning."""
    while True:
        config = load_config()
        console.print(CUSTOMIZE_MENU, style="yellow")
        console.print("  Choice: ", end="", style="bold white")
        
        try:
            choice = input().strip()
        except (KeyboardInterrupt, EOFError):
            break

        # ---------------------------------------------------------
        # OPTION 1: ADD / REMOVE CLEAN APPS
        # ---------------------------------------------------------
        if choice == "1":
            console.print("\n  [dim]💡 Tip: Unsure about the colors? Check the 'Help' option in the main menu first![/dim]")
            console.print("  [dim]Scouting PC...[/dim]")
            flagged = scan_discovery_processes(config)
            
            if config["user_kill_list"]:
                console.print(f"  [bold green]Your Custom Clean Targets:[/bold green] {list(config['user_kill_list'])}\n")
                
            render_discovery_table(flagged, mode="clean")
            
            console.print("  [bold cyan]To Add/Remove:[/bold cyan] Type the [cyan]# number[/cyan] or app name (e.g. spotify)")
            console.print("  Your input (or press Enter to cancel): ", end="")
            user_input = input().strip().lower()
            if not user_input: continue
            
            # Map input to app name and tier
            chosen_app = None
            target_tier = "neutral"
            
            try:
                idx = int(user_input)
                if 0 < idx <= len(flagged):
                    chosen_app = flagged[idx-1]["normal"]
                    target_tier = flagged[idx-1]["tier"]
            except ValueError:
                chosen_app = user_input.removesuffix(".exe")
                # If typed manually, we must assume neutral unless it's in our lists
                if chosen_app in config["user_protected"]: target_tier = "protected"
                elif chosen_app in config["user_kill_list"]: target_tier = "killable"

            if not chosen_app:
                console.print("  [red]Invalid selection.[/red]"); _pause(); continue

            # ENFORCE RULES
            if target_tier == "protected":
                console.print(f"\n  [red]🛑 SAFETY BLOCK: '{chosen_app}' is a protected app.[/red]")
                console.print("  You cannot add it to the clean list.")
            elif target_tier == "killable":
                if chosen_app in config["user_kill_list"]:
                    config["user_kill_list"].remove(chosen_app)
                    save_config(config["user_protected"], config["user_kill_list"], config["threshold_mb"])
                    console.print(f"\n  [yellow]✗ Removed '{chosen_app}' from custom clean list.[/yellow]")
                else:
                    console.print(f"\n  [yellow]⚠️ '{chosen_app}' is a DEFAULT system target.[/yellow]")
                    console.print("  To stop RamKleener from closing it, go to Option 2 and make it Safe.")
            else:
                config["user_kill_list"].add(chosen_app)
                save_config(config["user_protected"], config["user_kill_list"], config["threshold_mb"])
                console.print(f"\n  [green]✓ Added '{chosen_app}' to your clean targets![/green]")
            _pause()

        # ---------------------------------------------------------
        # OPTION 2: ADD / REMOVE SAFE APPS
        # ---------------------------------------------------------
        elif choice == "2":
            console.print("\n  [dim]💡 Tip: Unsure about the colors? Check the 'Help' option in the main menu first![/dim]")
            console.print("  [dim]Scouting PC...[/dim]")
            flagged = scan_discovery_processes(config)
            
            if config["user_protected"]:
                console.print(f"  [bold green]Your Custom Safe Apps:[/bold green] {list(config['user_protected'])}\n")
                
            render_discovery_table(flagged, mode="safe")
            
            console.print("  [bold cyan]To Add/Remove:[/bold cyan] Type the [cyan]# number[/cyan] or app name")
            console.print("  Your input (or press Enter to cancel): ", end="")
            user_input = input().strip().lower()
            if not user_input: continue
            
            chosen_app = None
            try:
                idx = int(user_input)
                if 0 < idx <= len(flagged):
                    chosen_app = flagged[idx-1]["normal"]
            except ValueError:
                chosen_app = user_input.removesuffix(".exe")

            if not chosen_app: continue

            # EXTRA CONFIRMATION LAYER
            action = "REMOVE from" if chosen_app in config["user_protected"] else "ADD to"
            console.print(f"\n  Are you sure you want to [bold]{action}[/bold] '{chosen_app}' safe list? (y/n): ", end="")
            confirm = input().strip().lower()
            
            if confirm == "y":
                if chosen_app in config["user_protected"]:
                    config["user_protected"].remove(chosen_app)
                    console.print(f"  [yellow]✗ '{chosen_app}' is no longer protected.[/yellow]")
                else:
                    config["user_protected"].add(chosen_app)
                    console.print(f"  [green]✓ '{chosen_app}' is now safely locked.[/green]")
                save_config(config["user_protected"], config["user_kill_list"], config["threshold_mb"])
            else:
                console.print("  [dim]Action cancelled.[/dim]")
            _pause()

        # ---------------------------------------------------------
        # OPTION 3: ADJUST RAM SIZE LIMIT
        # ---------------------------------------------------------
        elif choice == "3":
            console.print(f"\n  [bold]Current setting:[/bold] Ignore apps using less than {config['threshold_mb']} MB.")
            console.print("  Would you like to change this? (y/n): ", end="")
            if input().strip().lower() == "y":
                console.print("  Enter new size limit in MB (Range: 10 to 1024): ", end="")
                try:
                    new_val = int(input().strip())
                    if 10 <= new_val <= 1024:
                        save_config(config["user_protected"], config["user_kill_list"], new_val)
                        console.print(f"  [green]✓ Limit updated to {new_val} MB.[/green]")
                    else:
                        console.print("  [red]Value must be between 10 and 1024.[/red]")
                except ValueError:
                    console.print("  [red]Invalid number.[/red]")
            else:
                console.print("  [dim]Kept current threshold.[/dim]")
            _pause()

        elif choice == "0":
            break


def main():
    console.print("\n  [bold cyan]RamKleener[/bold cyan] — starting up...\n")

    while True:
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
            handle_customize()
        elif choice == "5":
            render_help()
            _pause()
        elif choice == "6":
            render_about()
            _pause()
        elif choice == "0":
            console.print("\n  [dim]Bye.[/dim]\n")
            break
        else:
            console.print("\n  [red]Invalid choice.[/red] Enter 0–6.\n")


if __name__ == "__main__":
    main()