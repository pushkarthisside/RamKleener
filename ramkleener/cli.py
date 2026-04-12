# ============================================================
#  cli.py — RamKleener v2.0
#  Entry point, menu loop, admin check, flow controller.
# ============================================================

import sys
import os
import platform
from rich.console import Console

from ramkleaner.config import load_config
from ramkleaner.cleaner import run_clean
from ramkleaner.display import (
    show_header,
    show_menu,
    show_help,
    show_about,
    show_ram_bar,
    show_bloat_table,
    show_clean_summary,
    run_scan_with_progress
)

console = Console()


# ── Admin Check ───────────────────────────────────────────────

def is_admin() -> bool:
    """
    Returns True if running with admin/root privileges.
    """
    try:
        if platform.system() == "Windows":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0
    except Exception:
        return False


# ── Confirmation Prompt ───────────────────────────────────────

def confirm_clean(bloat_list: list[dict]) -> bool:
    """
    Shows estimated impact and asks Y/N.
    """
    total_mb    = round(sum(p["mem_mb"] for p in bloat_list), 1)
    proc_count  = len(bloat_list)

    while True:
        console.print(
            f"\n  [yellow]Proceed with cleaning "
            f"[white]{proc_count}[/white] process(es) "
            f"(~[white]{total_mb} MB[/white])? "
            f"([white]y[/white]/[white]n[/white]): [/yellow]",
            end=""
        )
        choice = input().strip().lower()

        if choice == 'y':
            return True
        elif choice == 'n':
            console.print("  [dim]Cancelled.[/dim]\n")
            return False
        else:
            console.print("  [red]Invalid input. Enter y or n.[/red]")


# ── Post-Clean Pause ──────────────────────────────────────────

def pause() -> None:
    console.print("\n  [dim]Press Enter to return to menu...[/dim]", end="")
    input()


# ── Main ──────────────────────────────────────────────────────

def main() -> None:
    try:
        admin       = is_admin()
        config      = load_config()
        last_scan   = None  # stores last scan result for reuse

        # One-time header
        show_header(admin)

        while True:
            show_menu()

            console.print("  [cyan]> [/cyan]", end="")
            choice = input().strip()

            # ── Option 1: Scan ────────────────────────────────
            if choice == "1":
                last_scan, metadata = run_scan_with_progress(config)
                show_bloat_table(last_scan, metadata)

            # ── Option 2: Clean ───────────────────────────────
            elif choice == "2":
                if not last_scan:
                    console.print("  [dim]No scan yet — running scan first...[/dim]")
                    last_scan, metadata = run_scan_with_progress(config)
                    show_bloat_table(last_scan, metadata)

                if not last_scan:
                    console.print("  [green]Nothing to clean.[/green]\n")
                    continue

                if confirm_clean(last_scan):
                    summary = run_clean(last_scan, full_clean=False)
                    show_clean_summary(
                        killed        = summary["killed"],
                        already_gone  = summary["already_gone"],
                        denied        = summary["denied"],
                        other_fail    = summary["other_fail"],
                        est_impact_mb = summary["est_impact_mb"],
                        temp_deleted  = summary["temp_files"],
                        temp_mb       = summary["temp_mb"]
                    )
                    show_ram_bar()
                    last_scan = None
                    pause()

            # ── Option 3: Full Clean ──────────────────────────
            elif choice == "3":
                last_scan, metadata = run_scan_with_progress(config)
                show_bloat_table(last_scan, metadata)

                if not last_scan:
                    console.print("  [green]No bloat processes found.[/green]\n")
                    console.print("  [dim]Running temp cleanup & standby flush...[/dim]")
                    
                    summary = run_clean([], full_clean=True)
                    show_clean_summary(
                        killed        = summary["killed"],
                        already_gone  = summary["already_gone"],
                        denied        = summary["denied"],
                        other_fail    = summary["other_fail"],
                        est_impact_mb = summary["est_impact_mb"],
                        temp_deleted  = summary["temp_files"],
                        temp_mb       = summary["temp_mb"]
                    )
                    show_ram_bar()
                    pause()
                    continue

                if confirm_clean(last_scan):
                    summary = run_clean(last_scan, full_clean=True)
                    show_clean_summary(
                        killed        = summary["killed"],
                        already_gone  = summary["already_gone"],
                        denied        = summary["denied"],
                        other_fail    = summary["other_fail"],
                        est_impact_mb = summary["est_impact_mb"],
                        temp_deleted  = summary["temp_files"],
                        temp_mb       = summary["temp_mb"]
                    )
                    show_ram_bar()
                    last_scan = None
                    pause()

            # ── Option 4: Help ────────────────────────────────
            elif choice == "4":
                show_help()

            # ── Option 5: About ───────────────────────────────
            elif choice == "5":
                show_about()

            # ── Option 0: Exit ────────────────────────────────
            elif choice == "0":
                console.print("\n  [dim]Bye.[/dim]\n")
                sys.exit(0)

            # ── Invalid input ─────────────────────────────────
            else:
                console.print("  [red]Invalid option. Enter 0-5.[/red]\n")

    except KeyboardInterrupt:
        console.print("\n\n  [dim]Interrupted. Bye.[/dim]\n")
        sys.exit(0)


if __name__ == "__main__":
    main() 