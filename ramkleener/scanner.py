# ============================================================
#  scanner.py — RamKleener Process Scanner (v1.4 Final)
#  Stable, efficient, and production-ready baseline.
# ============================================================

import psutil
import platform
from ramkleener.config import get_effective_lists


def _normalize(name, is_windows):
    """
    Central normalization logic to keep config + runtime consistent.
    """
    name = name.lower().strip()
    if is_windows:
        name = name.removesuffix(".exe")
    return name


def scan_processes(config, debug=False):
    """
    Scans running processes and filters against the 2-tier safety model.
    """
    raw_protected, raw_kill_list = get_effective_lists(config)

    is_windows = platform.system() == "Windows"

    effective_protected = {_normalize(p, is_windows) for p in raw_protected}
    effective_kill_list = {_normalize(k, is_windows) for k in raw_kill_list}

    threshold_mb = config.get("threshold_mb", 10)

    flagged = []

    # Debug control (prevents console spam)
    debug_count = 0
    DEBUG_LIMIT = 50

    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            pinfo = proc.info
            raw_name = pinfo.get("name")
            mem_info = pinfo.get("memory_info")
            pid = pinfo.get("pid")

            if not raw_name or not mem_info:
                continue

            normalized = _normalize(raw_name, is_windows)

            # --- Tier 1: PROTECTED ---
            if normalized in effective_protected:
                if debug and debug_count < DEBUG_LIMIT:
                    print(f"[DEBUG] Skipping {raw_name} (PID {pid}): PROTECTED")
                    debug_count += 1
                continue

            # --- Tier 2: SAFE_TO_KILL ---
            if normalized in effective_kill_list:
                ram_mb = round(mem_info.rss / (1024 * 1024), 1)

                if ram_mb >= threshold_mb:
                    flagged.append({
                        "pid": pid,
                        "name": raw_name,
                        "normal": normalized,
                        "ram_mb": ram_mb
                    })
                elif debug and debug_count < DEBUG_LIMIT:
                    print(f"[DEBUG] Skipping {raw_name} (PID {pid}): Below {threshold_mb}MB")
                    debug_count += 1

                continue

            # --- UNKNOWN ---
            if debug and debug_count < DEBUG_LIMIT:
                print(f"[DEBUG] Skipping {raw_name} (PID {pid}): UNKNOWN")
                debug_count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    flagged.sort(key=lambda p: p["ram_mb"], reverse=True)
    return flagged


def get_system_ram():
    """
    Fetches global RAM stats for display/UI.
    """
    mem = psutil.virtual_memory()
    return {
        "total_mb": round(mem.total / (1024 * 1024), 1),
        "available_mb": round(mem.available / (1024 * 1024), 1),
        "used_mb": round(mem.used / (1024 * 1024), 1),
        "percent_used": mem.percent
    }