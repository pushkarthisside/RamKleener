# ============================================================
#  cleaner.py — RamKleener Kill Logic (v2.3 UI Uniformity)
# ============================================================

import psutil
from collections import defaultdict
from rich.console import Console

console = Console()

def _kill_process(proc):
    """Attempts to terminate a single process safely."""
    try:
        proc.terminate()
        proc.wait(timeout=3)
        return True, "killed"
    except psutil.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(timeout=3)
            return True, "force killed"
        except Exception as e:
            return False, f"force kill failed: {e}"
    except psutil.NoSuchProcess:
        return False, "already exited"
    except psutil.AccessDenied:
        return False, "access denied"
    except Exception as e:
        return False, str(e)


def _build_result(name, ram_mb, success, reason):
    return {
        "name":    name,
        "ram_mb":  ram_mb,
        "success": success,
        "reason":  reason
    }


def group_by_name(flagged):
    """Groups individual PIDs by their normalized process name."""
    groups = defaultdict(lambda: {
        "name":   "",
        "normal": "",
        "pids":   [],
        "ram_mb": 0.0,
        "count":  0
    })

    for proc in flagged:
        key = proc["normal"]
        groups[key]["name"]    = proc["name"]
        groups[key]["normal"]  = proc["normal"]
        groups[key]["pids"].append(proc["pid"])
        groups[key]["ram_mb"] += proc["ram_mb"]
        groups[key]["count"]  += 1

    result = list(groups.values())
    result.sort(key=lambda g: g["ram_mb"], reverse=True)
    return result


def kill_all(flagged):
    """Nuclear option: Kills every process found in the scan with clean UI."""
    if not flagged:
        return []

    console.print(f"\n  Found {len(flagged)} process(es). Kill all? [bold cyan](y/n)[/bold cyan]: ", end="")
    try:
        confirm = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        return []

    if confirm != "y":
        console.print("  [yellow]Cancelled.[/yellow]\n")
        return []

    results = []
    for proc_dict in flagged:
        try:
            proc = psutil.Process(proc_dict["pid"])
            if proc.name() != proc_dict["name"]:
                success, reason = False, "PID recycled (safe skip)"
            else:
                success, reason = _kill_process(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            success, reason = False, "inaccessible/exited"
        except Exception as e:
            success, reason = False, str(e)

        results.append(_build_result(
            proc_dict["name"], proc_dict["ram_mb"], success, reason
        ))

    return results


def kill_selective(groups):
    """
    Interactive mode: Steps through pre-computed grouped processes.
    No recomputation overhead.
    """
    if not groups:
        return []

    results = []
    total = len(groups)

    console.print()
    for i, group in enumerate(groups, start=1):
        name   = group["name"]
        ram_mb = group["ram_mb"]
        count  = group["count"]
        pids   = group["pids"]

        count_str = f"{count} PID{'s' if count > 1 else ''}"
        console.print(
            f"  [{i}/{total}] [white]{name:<25}[/white] [cyan]{count_str:<10}[/cyan] "
            f"[yellow]{ram_mb:.1f} MB total[/yellow] — kill? [bold cyan](y/n/q)[/bold cyan]: ", end=""
        )
        try:
            answer = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if answer == "q":
            console.print("  [dim]Quitting interactive mode.[/dim]\n")
            break

        if answer != "y":
            console.print("  [dim]→ skipped[/dim]")
            results.append(_build_result(name, ram_mb, False, "skipped by user"))
            continue

        any_success = False
        last_reason = "killed"

        for pid in pids:
            try:
                proc = psutil.Process(pid)
                if proc.name() != name:
                    success, reason = False, "PID recycled"
                else:
                    success, reason = _kill_process(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                success, reason = False, "inaccessible"

            if success:
                any_success = True
            else:
                last_reason = reason

        group_success = any_success
        group_reason  = "killed" if any_success else last_reason

        if group_success:
            console.print("  [green]→ ✓ killed[/green]")
        else:
            console.print(f"  [red]→ ✗ {group_reason}[/red]")

        results.append(_build_result(name, ram_mb, group_success, group_reason))

    console.print()
    return results