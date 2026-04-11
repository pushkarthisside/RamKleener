# ============================================================
#  RamKleener v1.0  |  by Pushkar
# ============================================================

# --- TIER 1: LOCKED FOREVER ---
$NEVER_KILL_CORE = @(
    "System", "smss", "csrss", "wininit", "winlogon",
    "services", "lsass", "dwm", "explorer", "svchost",
    "taskmgr", "powershell", "pwsh", "cmd", "conhost"
)

# --- TIER 2: PROTECTED BY DEFAULT ---
$NEVER_KILL_DEFAULT = @(
    "vgc", "vgtray", "VALORANT", "VALORANT-Win64-Shipping",
    "RiotClientServices", "RiotClientUx", "RiotClientUxRender",
    "MsMpEng", "NisSrv", "SecurityHealthService",
    "Steam", "steamwebhelper", "EpicGamesLauncher", "Battle.net"
)

# --- TIER 3: SAFE TO KILL ---
$SAFE_TO_KILL = @(
    "chrome", "msedge", "msedgewebview2", "browser_broker",
    "GoogleUpdate", "GoogleCrashHandler", "GoogleCrashHandler64",
    "MicrosoftEdgeUpdate",
    "OneDrive",
    "AdobeIPCBroker", "AdobeUpdateService", "AGMService", "armsvc",
    "compattelrunner", "MusNotification", "MusNotifyIcon",
    "SpotifyWebHelper", "DiscordCrashService",
    "msteams", "ms-teams", "CefSharp.BrowserSubprocess", "Widgets"
)

# ============================================================
#  STEP 2: RAM STATS + VISUAL BAR
# ============================================================

function Get-RAMStats {
    $os    = Get-CimInstance Win32_OperatingSystem
    $total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $free  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $used  = [math]::Round($total - $free, 2)
    $pct   = [math]::Round(($used / $total) * 100, 0)
    return @{ Total=$total; Free=$free; Used=$used; Pct=$pct }
}

function Draw-RAMBar {
    param($pct)
    $barLen    = 40
    $filled    = [int][math]::Round($pct / 100 * $barLen)
    $empty     = $barLen - $filled
    $filledBar = New-Object String([char]0x2588, $filled)
    $emptyBar  = New-Object String([char]0x2591, $empty)
    $color     = if ($pct -ge 85) { "Red" } `
                 elseif ($pct -ge 65) { "Yellow" } `
                 else { "Green" }
    Write-Host "  RAM  [" -NoNewline -ForegroundColor White
    Write-Host $filledBar -NoNewline -ForegroundColor $color
    Write-Host $emptyBar -NoNewline -ForegroundColor DarkGray
    Write-Host "]  $pct%" -ForegroundColor $color
}

function Show-RAMStats {
    $r = Get-RAMStats
    Write-Host ""
    Write-Host "  +-- MEMORY -----------------------------------------+" -ForegroundColor DarkCyan
    Draw-RAMBar $r.Pct
    Write-Host "  Total: $($r.Total) GB   Used: $($r.Used) GB   Free: $($r.Free) GB" -ForegroundColor Gray
    Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
    Write-Host ""
    return $r
}

# --- TEST (remove after confirming it works) ---
Show-RAMStats