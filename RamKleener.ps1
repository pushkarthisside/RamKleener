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

# ============================================================
#  STEP 5: CLEANER — KILL + TEMP CLEAR
# ============================================================

function Invoke-Cleaner {
    param(
        [System.Collections.Generic.List[PSCustomObject]]$Processes
    )

    $killed      = 0
    $alreadyGone = 0
    $denied      = 0
    $otherFail   = 0
    $estImpactMB = 0

    Write-Host ""
    Write-Host "  Cleaning $($Processes.Count) process(es)..." -ForegroundColor DarkGray
    Write-Host "  +-- CLEANING ----------------------------------------+" -ForegroundColor DarkCyan

    # --- KILL LOOP ---
    foreach ($proc in $Processes) {

        # Guard: skip malformed entries
        if (-not $proc.PID -or -not $proc.Name) { continue }

        try {
            Stop-Process -Id $proc.PID -ErrorAction Stop

            $killed      += 1
            $estImpactMB += $proc.MemMB
            Write-Host "  " -NoNewline
            Write-Host "[OK]" -NoNewline -ForegroundColor Green
            Write-Host " Killed $($proc.Name) (PID $($proc.PID)) — $($proc.MemMB) MB" -ForegroundColor White

        } catch {
            $msg = $_.Exception.Message

            if ($msg -match "Cannot find a process" -or $msg -match "process with process id") {
                $alreadyGone += 1
                Write-Host "  " -NoNewline
                Write-Host "[--]" -NoNewline -ForegroundColor Yellow
                Write-Host " Already closed — $($proc.Name)" -ForegroundColor DarkGray

            } elseif ($msg -match "Access is denied") {
                $denied += 1
                Write-Host "  " -NoNewline
                Write-Host "[!!]" -NoNewline -ForegroundColor Red
                Write-Host " Access denied — $($proc.Name) (Run as Admin?)" -ForegroundColor Red

            } else {
                $otherFail += 1
                Write-Host "  " -NoNewline
                Write-Host "[??]" -NoNewline -ForegroundColor DarkGray
                Write-Host " Failed — $($proc.Name): $msg" -ForegroundColor DarkGray
            }
        }
    }

    # --- TEMP FILE CLEAR ---
    Write-Host ""
    Write-Host "  Clearing temp files..." -ForegroundColor DarkGray

    $tempPaths   = @($env:TEMP, "$env:SystemRoot\Temp")
    $tempDeleted = 0
    $tempMB      = 0

    foreach ($path in $tempPaths) {
        if (-not (Test-Path $path)) { continue }

        $files = Get-ChildItem -Path $path -File -Recurse -Force -ErrorAction SilentlyContinue

        foreach ($file in $files) {
            try {
                $size = $file.Length / 1MB
                Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                $tempMB      += $size      # only counted if delete succeeded
                $tempDeleted += 1
            } catch {
                continue
            }
        }
    }

    $tempMB = [math]::Round($tempMB, 1)
    Write-Host "  " -NoNewline
    Write-Host "[OK]" -NoNewline -ForegroundColor Green
    Write-Host " Temp cleared — $tempDeleted files / $tempMB MB" -ForegroundColor White

    # --- SUMMARY ---
    Write-Host ""
    Write-Host "  +-- SUMMARY ----------------------------------------+" -ForegroundColor DarkCyan
    Write-Host "  Killed:             $killed process(es)" -ForegroundColor White
    Write-Host "  Est. memory impact: $estImpactMB MB" -ForegroundColor Cyan
    Write-Host "  Temp files removed: $tempDeleted ($tempMB MB)" -ForegroundColor Cyan
    if ($denied -gt 0) {
        Write-Host "  Access denied:      $denied (Try running as Admin)" -ForegroundColor Red
    }
    Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
    Write-Host ""
}

# --- TEST (remove after confirming it works) ---
$results = Get-BloatProcesses
Show-BloatTable $results
Invoke-Cleaner $results