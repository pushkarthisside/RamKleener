# ============================================================
#  RamKleener v1.0  |  by Pushkar
#  github.com/yourhandle/RamKleener
# ============================================================

# --- TIER 1: LOCKED FOREVER ---
# Windows cannot function without these. Never editable.
$NEVER_KILL_CORE = @(
    "System", "smss", "csrss", "wininit", "winlogon",
    "services", "lsass", "dwm", "explorer", "svchost",
    "taskmgr", "powershell", "pwsh", "cmd", "conhost"
)

# --- TIER 2: PROTECTED BY DEFAULT ---
# Safe critical apps. Protected out of the box.
# In Phase 2 users can override these via config file.
$NEVER_KILL_DEFAULT = @(
    # Riot / Valorant — anti-cheat runs even when game is closed
    "vgc", "vgtray", "VALORANT", "VALORANT-Win64-Shipping",
    "RiotClientServices", "RiotClientUx", "RiotClientUxRender",
    # Windows Defender
    "MsMpEng", "NisSrv", "SecurityHealthService",
    # Game launchers
    "Steam", "steamwebhelper", "EpicGamesLauncher", "Battle.net"
)

# --- TIER 3: SAFE TO KILL ---
# Known background bloat. These get killed when you clean.
$SAFE_TO_KILL = @(
    # Browser background workers
    "chrome", "msedge", "msedgewebview2", "browser_broker",
    # Browser updaters / crash handlers
    "GoogleUpdate", "GoogleCrashHandler", "GoogleCrashHandler64",
    "MicrosoftEdgeUpdate",
    # OneDrive sync daemon
    "OneDrive",
    # Adobe background garbage
    "AdobeIPCBroker", "AdobeUpdateService", "AGMService", "armsvc",
    # Windows telemetry
    "compattelrunner", "MusNotification", "MusNotifyIcon",
    # Misc
    "SpotifyWebHelper", "DiscordCrashService"
)
# Modern bloat (added from review)
    "msteams", "ms-teams",
    "CefSharp.BrowserSubprocess",
    "Widgets"