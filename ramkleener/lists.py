# ============================================================
#  lists.py — RamKleener Process Lists (v1.3 Meta)
# ============================================================

# PROTECTED: Locked forever. Hardcoded safety.
# Rule: If it's here, it CANNOT be in SAFE_TO_KILL.
PROTECTED = {
    # --- OS CORE: Windows ---
    "system",                # Hardware-level kernel process
    "smss",                  # Session Manager Subsystem
    "csrss",                 # Client/Server Runtime Process
    "wininit",               # Windows Initialization
    "winlogon",              # User Login handling
    "services",              # Service Control Manager
    "lsass",                 # Local Security Authority (Crucial)
    "dwm",                   # Desktop Window Manager (The UI)
    "explorer",              # Taskbar and File Explorer
    "svchost",               # Generic Host Process for Win Services
    "taskmgr",               # Task Manager
    "powershell", "pwsh",    # Terminal shells
    "cmd", "conhost",        # Command prompt and console host

    # --- SECURITY & ANTI-CHEAT ---
    "msmpeng", "nissrv",     # Microsoft Defender / Antivirus
    "securityhealthservice", # Windows Security Health
    "vgc", "vgtray",         # Riot Vanguard (Valorant)
    "valorant",              # Main game process

    # --- GAMING LAUNCHERS (Protect to avoid logout/crash) ---
    "steam", "steamwebhelper",
    "epicgameslauncher",
    "battle.net",
    "riotclientservices", "riotclientux", "riotclientuxrender",

    # --- SELF-PROTECTION (Essential) ---
    "python", "python3", "pythonw", # Don't kill the interpreter!
    "ramkleener",                   # Don't kill this script!
}

# SAFE_TO_KILL: Explicitly named bloat. 
# Only processes found here (or in validated user config) get terminated.
SAFE_TO_KILL = {
    # --- BROWSERS & WEB VIEWERS ---
    "chrome",                # Google Chrome
    "msedge",                # Microsoft Edge
    "msedgewebview2",        # Edge-based web rendering in apps
    "browser_broker",        # Browser helper
    "brave",                 # Brave Browser
    "bravecrashhandler",     # Brave error reporter

    # --- UPDATERS (Silent RAM eaters) ---
    "googleupdate",          # Google services updater
    "googlecrashhandler",    # Google crash reporter
    "googlecrashhandler64",
    "microsoftedgeupdate",   # Edge browser updater
    "adobeupdateservice",    # Adobe background updates
    "armsvc",                # Adobe Acrobat Update Service

    # --- CLOUD & SYNC ---
    "onedrive",              # Microsoft Cloud Sync
    "dropbox",               # Dropbox background sync
    "adobeipcbroker",        # Adobe Creative Cloud sync helper

    # --- COMMUNICATION & OFFICE ---
    "msteams", "ms-teams",   # Microsoft Teams (Famous RAM hog)
    "discordcrashservice",   # Discord background helper
    "slack",                 # Slack desktop app
    "whatsapp.root",         # WhatsApp background process
    "notion",                # Notion desktop background helpers

    # --- TELEMETRY & BLOAT ---
    "compattelrunner",       # Windows Compatibility Telemetry (Heavy)
    "musnotification",       # Windows Update notifications
    "musnotifyicon",
    "widgets",               # Windows 11 Widgets panel
    "spotifywebhelper",      # Spotify background helper
    "cefsharp.browsersubprocess", # Generic embedded browser bloat
    "agmservice",            # Adobe Genuine Monitor

    # --- OEM BLOAT (Laptop specific) ---
    "omencommandcenterbackground", # HP Omen background
    "omenring",                   # HP Omen lighting
}