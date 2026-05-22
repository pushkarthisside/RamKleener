# ============================================================
#  cleaner.py — RamKleener v2.0
#  Kill engine, temp cleanup, standby RAM flush.
#  Returns summary dict — display is handled by cli.py
# ============================================================

import os
import sys
import time
import tempfile
import platform
import psutil
from pathlib import Path
from rich.console import Console
from rich.markup import escape  # FIX 1: Import escape for safety

console = Console()


# ── Kill Processes ────────────────────────────────────────────

def kill_processes(bloat_list: list[dict]) -> dict:
    """
    Iterates bloat_list, terminates each process by PID.
    Prints live feedback per process.
    Returns kill stats dict.
    """
    killed       = 0
    already_gone = 0
    denied       = 0
    other_fail   = 0
    est_impact   = 0.0

    console.print()
    console.print(f"  [dim]Cleaning {len(bloat_list)} process(es)...[/dim]")
    console.print()

    for proc_info in bloat_list:

        # Guard: skip malformed entries
        if not proc_info.get("pid") or not proc_info.get("name"):
            continue

        pid    = proc_info["pid"]
        name   = proc_info["name"]
        mem_mb = proc_info["mem_mb"]
        
        safe_name = escape(name)  # FIX 1: Escape name for Rich

        try:
            proc = psutil.Process(pid)
            proc.terminate()

            # Wait up to 3 seconds for clean exit
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                # Didn't die cleanly — force kill
                proc.kill()

            killed      += 1
            est_impact += mem_mb
            console.print(
                f"  [green][OK][/green] Killed [white]{safe_name}[/white]"
                f" (PID {pid}) — [cyan]{mem_mb} MB[/cyan]"
            )

        except psutil.NoSuchProcess:
            already_gone += 1
            console.print(
                f"  [dim][--] Already closed — {safe_name}[/dim]"
            )

        except psutil.AccessDenied:
            denied += 1
            console.print(
                f"  [red][!!] Access denied — {safe_name} (Run as Admin?)[/red]"
            )

        except Exception as e:
            other_fail += 1
            console.print(
                f"  [dim][??] Failed — {safe_name}: {e}[/dim]"
            )

    return {
        "killed":       killed,
        "already_gone": already_gone,
        "denied":       denied,
        "other_fail":   other_fail,
        "est_impact_mb": round(est_impact, 1)
    }


# ── Clear Temp Files ──────────────────────────────────────────

def clear_temp() -> dict:
    """
    Deletes files from user temp and system temp.
    Skips locked files silently.
    Returns temp cleanup stats dict.
    """
    temp_paths = set()

    # User temp — cross-platform
    temp_paths.add(Path(tempfile.gettempdir()))

    # Windows system temp
    if platform.system() == "Windows":
        sys_temp = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp"
        temp_paths.add(sys_temp)

    files_deleted = 0
    bytes_cleared = 0.0

    console.print()
    console.print("  [dim]Clearing temp files...[/dim]")

    for temp_path in temp_paths:
        if not temp_path.exists():
            continue
        
        # rglob can occasionally throw a permission error on the root iterator itself in Windows.
        try:
            for file in temp_path.rglob("*"):
                # FIX 2: Move everything inside the try block to catch deep permission errors
                try:
                    if not file.is_file():
                        continue
                    size = file.stat().st_size
                    file.unlink()
                    bytes_cleared += size
                    files_deleted += 1
                except Exception:
                    # Locked, in-use, or permission denied — skip silently
                    continue
        except Exception:
            # If the entire directory is locked from scanning, skip it
            continue

    mb_cleared = round(bytes_cleared / (1024 * 1024), 1)

    console.print(
        f"  [green][OK][/green] Temp cleared — "
        f"[white]{files_deleted}[/white] files / "
        f"[cyan]{mb_cleared} MB[/cyan]"
    )

    return {
        "files_deleted": files_deleted,
        "mb_cleared":    mb_cleared
    }


# ── Flush Standby RAM (Windows only) ─────────────────────────

def flush_standby_list() -> bool:
    """
    Flushes the Windows standby RAM list via ctypes.
    Requires Admin. Returns True on success, False otherwise.
    No-op on non-Windows systems.
    """
    if platform.system() != "Windows":
        return False

    try:
        import ctypes
        from ctypes import wintypes
        
        # FIX 3: Windows API requires explicitly enabling the token privilege first
        advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        TOKEN_ADJUST_PRIVILEGES = 0x0020
        TOKEN_QUERY = 0x0008
        SE_PRIVILEGE_ENABLED = 0x00000002
        
        class LUID(ctypes.Structure):
            _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]
            
        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", wintypes.DWORD),
                        ("Privileges", LUID),
                        ("Attributes", wintypes.DWORD)]
        
        hToken = wintypes.HANDLE()
        if advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(hToken)):
            luid = LUID()
            if advapi32.LookupPrivilegeValueW(None, "SeProfileSingleProcessPrivilege", ctypes.byref(luid)):
                tp = TOKEN_PRIVILEGES()
                tp.PrivilegeCount = 1
                tp.Privileges = luid
                tp.Attributes = SE_PRIVILEGE_ENABLED
                # Enable the privilege
                advapi32.AdjustTokenPrivileges(hToken, False, ctypes.byref(tp), ctypes.sizeof(tp), None, None)
            kernel32.CloseHandle(hToken)

        # MemoryPurgeStandbyList = 4
        result = ctypes.windll.ntdll.NtSetSystemInformation(
            80,      # SystemMemoryListInformation
            ctypes.byref(ctypes.c_int(4)),
            ctypes.sizeof(ctypes.c_int(4))
        )

        if result == 0:
            console.print(
                "  [green][OK][/green] Standby RAM flushed"
            )
            return True
        else:
            console.print(
                "  [yellow][--] Standby flush failed — Admin required[/yellow]"
            )
            return False

    except Exception as e:
        console.print(
            f"  [dim][??] Standby flush error: {e}[/dim]"
        )
        return False


# ── Main Clean Entry Point ────────────────────────────────────

def run_clean(bloat_list: list[dict], full_clean: bool = False) -> dict:
    """
    Orchestrates the full clean sequence.
    Called by cli.py — returns summary dict for display.

    Args:
        bloat_list  — from scanner.scan_processes()
        full_clean  — if True, also flushes standby RAM
    """
    kill_stats = kill_processes(bloat_list)
    temp_stats = clear_temp()

    standby_flushed = False
    if full_clean and platform.system() == "Windows":
        standby_flushed = flush_standby_list()

    return {
        "killed":           kill_stats["killed"],
        "already_gone":     kill_stats["already_gone"],
        "denied":           kill_stats["denied"],
        "other_fail":       kill_stats["other_fail"],
        "est_impact_mb":    kill_stats["est_impact_mb"],
        "temp_files":       temp_stats["files_deleted"],
        "temp_mb":          temp_stats["mb_cleared"],
        "standby_flushed":  standby_flushed
    }