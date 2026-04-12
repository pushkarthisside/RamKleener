# ============================================================
#  scanner.py — RamKleener v2.0
#  Scans all running processes, applies three-tier safety model,
#  filters by threshold, returns bloat list + scan metadata.
# ============================================================

import os
import psutil

from ramkleaner.lists import NEVER_KILL_CORE
from ramkleaner.config import get_protected_set, get_kill_set, get_threshold


def scan_processes(config: dict) -> tuple[list[dict], dict]:
    """
    Scans all running processes and filters against the three-tier model.

    Returns:
        bloat_list  — list of dicts: {name, pid, mem_mb}
        metadata    — dict: {total_scanned, total_bloat_mem, threshold_used}
    """

    protected_set = get_protected_set(config)   # NEVER_KILL_DEFAULT + user_protected
    kill_set      = get_kill_set(config)         # SAFE_TO_KILL + user_kill_list
    threshold     = get_threshold(config)        # minimum MB to include

    current_pid   = os.getpid()                  # self-exclusion by PID

    bloat_list    = []
    total_scanned = 0
    total_bloat_mem = 0.0

    # OPTIMIZATION: Fetch required attributes in one go for speed
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # When using attrs in process_iter, data is accessed via .info dict
            pinfo = proc.info
            
            # Some OS-level processes might have a None name or memory_info, skip them
            if not pinfo['name'] or not pinfo['memory_info']:
                continue

            name = pinfo['name'].lower()
            pid  = pinfo['pid']

            total_scanned += 1

            # --- THREE-TIER FILTER ---

            # Self-exclusion by PID (primary defense)
            if pid == current_pid:
                continue

            # Tier 1: NEVER_KILL_CORE — locked forever
            if name in NEVER_KILL_CORE:
                continue

            # Tier 2: NEVER_KILL_DEFAULT + user_protected
            if name in protected_set:
                continue

            # Only proceed if in kill set
            if name not in kill_set:
                continue

            # --- MEMORY CHECK ---
            mem_mb = round(pinfo['memory_info'].rss / (1024 * 1024), 1)

            # Threshold filter
            if mem_mb < threshold:
                continue

            bloat_list.append({
                "name":   name,
                "pid":    pid,
                "mem_mb": mem_mb
            })

            total_bloat_mem += mem_mb

        except psutil.AccessDenied:
            # Protected process — skip silently
            continue

        except psutil.NoSuchProcess:
            # Process died during scan — skip silently
            continue

        except Exception:
            # Any other OS-level error — never crash the scan
            continue

    # Sort by memory descending — heaviest bloat first
    bloat_list.sort(key=lambda x: x["mem_mb"], reverse=True)

    metadata = {
        "total_scanned":    total_scanned,
        "total_bloat_mem":  round(total_bloat_mem, 1),
        "threshold_used":   threshold
    }

    return bloat_list, metadata