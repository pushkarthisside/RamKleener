# ============================================================
#  lists.py — RamKleener v2.0
#  Three-tier process protection model
#  All names lowercase — normalization happens at scan time
# ============================================================

# TIER 1: LOCKED FOREVER — no one can edit this
# Critical OS processes. Killing any of these = system crash.
NEVER_KILL_CORE = {
    # Windows core
    "system", "smss", "csrss", "wininit", "winlogon",
    "services", "lsass", "dwm", "explorer", "svchost",
    "taskmgr", "powershell", "pwsh", "cmd", "conhost",
    # Linux core
    "init", "systemd", "kthreadd", "migration", "watchdog",
    "kworker", "ksoftirqd", "rcu_sched",
    # Mac core
    "launchd", "kernel_task", "loginwindow", "windowserver",
    # Self-Protection
    "python", "python3", "pythonw", "ramkleaner"
}

# TIER 2: PROTECTED BY DEFAULT — user can remove via config
# Games, launchers, security tools. Safe to keep, risky to kill blindly.
NEVER_KILL_DEFAULT = {
    # Riot / Valorant
    "vgc", "vgtray", "valorant", "valorant-win64-shipping",
    "riotclientservices", "riotclientux", "riotclientuxrender",
    # Windows security
    "msmpeng", "nissrv", "securityhealthservice",
    # Game launchers
    "steam", "steamwebhelper", "epicgameslauncher", "battle.net",
}

# TIER 3: SAFE TO KILL — known bloat, user can extend via config
SAFE_TO_KILL = {
    # Browsers
    "chrome", "msedge", "msedgewebview2", "browser_broker",
    # Google updaters
    "googleupdate", "googlecrashhandler", "googlecrashhandler64",
    # Microsoft updaters
    "microsoftedgeupdate",
    # Cloud
    "onedrive",
    # Adobe
    "adobeipcbroker", "adobeupdateservice", "agmservice", "armsvc",
    # Windows telemetry
    "compattelrunner", "musnotification", "musnotifyicon",
    # Apps
    "spotifywebhelper", "discordcrashservice",
    "msteams", "ms-teams", "cefsharp.browsersubprocess", "widgets",
    # Brave browser
    "brave",
    "bravecrashhandler",
    "bravecrashhandler64",

    # WhatsApp
    "whatsapp.root",

    # OMEN
    "omencommandcenterbackground",
    "omenring",
}