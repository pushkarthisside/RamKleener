# ============================================================
#  cleaner.py — RamKleener Kill Logic
#  v1.3 Meta: Two modes (Bulk & Selective), PID-recycling protection,
#  and group-based termination for multi-process apps (Browsers).
# ============================================================

import psutil
from collections import defaultdict


def _kill_process(proc):
    """
    Attempts to terminate a single process safely.
    Tries terminate() first, then kill() if it lingers.
    """
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
    """Builds a standardized result dict for display.py summary."""
    return {
        "name":    name,
        "ram_mb":  ram_mb,
        "success": success,
        "reason":  reason
    }


def group_by_name(flagged):
    """
    Groups individual PIDs by their normalized process name.
    Ensures users make one decision per app (e.g., 'Chrome') rather than per PID.
    """
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

    # Return as a list sorted by total RAM impact (heaviest groups first)
    result = list(groups.values())
    result.sort(key=lambda g: g["ram_mb"], reverse=True)
    return result


def kill_all(flagged):
    """
    Nuclear option: Kills every process found in the scan.
    """
    if not flagged:
        return []

    print(f"\n  Found {len(flagged)} process(es). Kill all? [y/n] ", end="")
    confirm = input().strip().lower()

    if confirm != "y":
        print("  Cancelled.\n")
        return []

    results = []
    for proc_dict in flagged:
        try:
            proc = psutil.Process(proc_dict["pid"])
            
            # PID Recycling Protection: Verify name hasn't changed since scan
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


def kill_selective(flagged):
    """
    Interactive mode: Steps through grouped processes.
    One decision per app name.
    """
    if not flagged:
        return [], []

    groups = group_by_name(flagged)
    results = []
    total = len(groups)

    print()
    for i, group in enumerate(groups, start=1):
        name   = group["name"]
        ram_mb = group["ram_mb"]
        count  = group["count"]
        pids   = group["pids"]

        count_str = f"{count} PID{'s' if count > 1 else ''}"
        print(
            f"  [{i}/{total}] {name:<25} {count_str:<10} "
            f"{ram_mb:.1f} MB total — kill? [y/n/q] ", end=""
        )
        answer = input().strip().lower()

        if answer == "q":
            print("  Quitting interactive mode.\n")
            break

        if answer != "y":
            print("  → skipped")
            results.append(_build_result(name, ram_mb, False, "skipped by user"))
            continue

        # Kill all PIDs associated with this name
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

        # Group succeeds if at least one PID was killed
        group_success = any_success
        group_reason  = "killed" if any_success else last_reason

        if group_success:
            print("  → ✓ killed")
        else:
            print(f"  → ✗ {group_reason}")

        results.append(_build_result(name, ram_mb, group_success, group_reason))

    print()
    return results, groups