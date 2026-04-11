# ============================================================
#  RamKleener v1.0  |  by Pushkar
# ============================================================

# --- TIER 1: LOCKED FOREVER ---
$NEVER_KILL_CORE = @(
    "system", "smss", "csrss", "wininit", "winlogon",
    "services", "lsass", "dwm", "explorer", "svchost",
    "taskmgr", "powershell", "pwsh", "cmd", "conhost"
)

# --- TIER 2: PROTECTED BY DEFAULT ---
$NEVER_KILL_DEFAULT = @(
    "vgc", "vgtray", "valorant", "valorant-win64-shipping",
    "riotclientservices", "riotclientux", "riotclientuxrender",
    "msmpeng", "nissrv", "securityhealthservice",
    "steam", "steamwebhelper", "epicgameslauncher", "battle.net"
)

# --- TIER 3: SAFE TO KILL ---

$SAFE_TO_KILL = @(
    "chrome", "msedge", "msedgewebview2", "browser_broker",
    "googleupdate", "googlecrashhandler", "googlecrashhandler64",
    "microsoftedgeupdate",
    "onedrive",
    "adobeipcbroker", "adobeupdateservice", "agmservice", "armsvc",
    "compattelrunner", "musnotification", "musnotifyicon",
    "spotifywebhelper", "discordcrashservice",
    "msteams", "ms-teams", "cefsharp.browsersubprocess", "widgets"
)

$thresholdMB = 50

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

function Get-BloatProcesses {
    $running    = Get-Process -ErrorAction SilentlyContinue
    $found      = New-Object System.Collections.Generic.List[PSCustomObject]
    $currentPid = $PID

    foreach ($proc in $running) {
        try {
            $name = $proc.Name.ToLower()   # FIX 1: lowercase normalization restored
            $id   = $proc.Id

            if ($id -eq $currentPid) { continue }
            if ($NEVER_KILL_CORE -contains $name) { continue }
            if ($NEVER_KILL_DEFAULT -contains $name) { continue }

            if ($SAFE_TO_KILL -contains $name) {
                $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 1)
                if ($memMB -lt $thresholdMB) { continue }   # FIX 2: threshold restored
                $found.Add([PSCustomObject]@{
                    Name  = $name
                    PID   = $id
                    MemMB = $memMB
                })
            }
        } catch {
            continue
        }
    }

    return $found | Sort-Object MemMB -Descending
}

# ============================================================
#  STEP 4: DISPLAY BLOAT TABLE
# ============================================================

function Show-BloatTable {
    param(
        [System.Collections.Generic.List[PSCustomObject]]$Processes
    )

    Write-Host ""
    Write-Host "  +-- BLOAT PROCESSES ---------------------------------+" -ForegroundColor DarkCyan

    if ($Processes.Count -eq 0) {
        Write-Host "  No bloat processes found above threshold." -ForegroundColor Green
        Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host ""
        return
    }

    # --- GROUP by process name, sum memory, count instances ---
    $grouped = $Processes | Group-Object -Property Name | ForEach-Object {
        [PSCustomObject]@{
            Name      = $_.Name
            Instances = $_.Count
            TotalMB   = [math]::Round(($_.Group | Measure-Object -Property MemMB -Sum).Sum, 1)
        }
    } | Sort-Object TotalMB -Descending

    # --- Column headers ---
    Write-Host ("  {0,-24} {1,-8} {2}" -f "Name", "Inst", "Memory (MB)") -ForegroundColor Gray
    Write-Host "  +------------------------+--------+---------------+" -ForegroundColor DarkGray

    # --- Rows ---
    foreach ($row in $grouped) {
        $memColor = if ($row.TotalMB -ge 200) { "Red" }
                    elseif ($row.TotalMB -ge 100) { "Yellow" }
                    else { "White" }

        $nameCol = "  {0,-24}" -f $row.Name
        $instCol = " x{0,-7}" -f $row.Instances

        Write-Host $nameCol -NoNewline -ForegroundColor White
        Write-Host $instCol -NoNewline -ForegroundColor DarkGray
        Write-Host ("{0,8} MB" -f $row.TotalMB) -ForegroundColor $memColor
    }

    # --- Totals ---
    $totalMB      = [math]::Round(($grouped | Measure-Object -Property TotalMB -Sum).Sum, 1)
    $totalProcs   = $Processes.Count
    $totalMemColor = if ($totalMB -ge 500) { "Red" } elseif ($totalMB -ge 200) { "Yellow" } else { "White" }

    Write-Host "  +------------------------+--------+---------------+" -ForegroundColor DarkGray
    Write-Host "  Total bloat RAM: " -NoNewline -ForegroundColor Gray
    Write-Host "$totalMB MB" -NoNewline -ForegroundColor $totalMemColor
    Write-Host "  across $totalProcs processes" -ForegroundColor DarkGray
    Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
    Write-Host ""
}

# --- TEST (remove after confirming it works) ---
$results = Get-BloatProcesses
Show-BloatTable $results