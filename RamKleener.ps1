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
}


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
        Show-RAMStats

}

    # ============================================================
    #  STEP 6: MENU LOOP + ADMIN CHECK
    # ============================================================

    function Test-Admin {
        $identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($identity)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }

    function Show-Header {
        Clear-Host
        Write-Host ""
        Write-Host "  +===================================================+" -ForegroundColor Cyan
        Write-Host "  |          RamKleener v1.0  |  by Pushkar           |" -ForegroundColor Cyan
        Write-Host "  +===================================================+" -ForegroundColor Cyan

        if (-not (Test-Admin)) {
            Write-Host "  [!] Not running as Admin — some kills may be denied." -ForegroundColor Yellow
        }

        Show-RAMStats
    }

    function Show-Menu {
        Write-Host "  +-- MENU -------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host "  1.  Scan processes" -ForegroundColor White
        Write-Host "  2.  Clean RAM  (kill bloat + clear temp)" -ForegroundColor White
        Write-Host "  3.  Full clean (kill + temp + show RAM after)" -ForegroundColor White
        Write-Host "  4.  Help" -ForegroundColor White
        Write-Host "  5.  About" -ForegroundColor White
        Write-Host "  0.  Exit" -ForegroundColor DarkGray
        Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host ""
    }

    function Show-Help {
        Write-Host ""
        Write-Host "  +-- HELP -------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host "  RamKleener scans for known memory-bloating processes" -ForegroundColor Gray
        Write-Host "  and kills them safely using a 3-tier protection model." -ForegroundColor Gray
        Write-Host ""
        Write-Host "  TIER 1 — NEVER_KILL_CORE   : locked forever (OS critical)" -ForegroundColor Red
        Write-Host "  TIER 2 — NEVER_KILL_DEFAULT: protected by default (games, AV)" -ForegroundColor Yellow
        Write-Host "  TIER 3 — SAFE_TO_KILL      : known bloat, killed if found" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Threshold: only kills processes using > $thresholdMB MB" -ForegroundColor Gray
        Write-Host "  Run as Admin for best results." -ForegroundColor Gray
        Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host ""
    }

    function Show-About {
        Write-Host ""
        Write-Host "  +-- ABOUT ------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host "  RamKleener v1.0" -ForegroundColor White
        Write-Host "  Built by Pushkar" -ForegroundColor Gray
        Write-Host "  Phase 1: PowerShell  |  Phase 2: Python (coming)" -ForegroundColor Gray
        Write-Host "  https://github.com/pushkar/RamKleener" -ForegroundColor DarkGray
        Write-Host "  +---------------------------------------------------+" -ForegroundColor DarkCyan
        Write-Host ""
    }

    function Invoke-ScanOnly {
        Write-Host ""
        Write-Host "  Scanning..." -ForegroundColor DarkGray
        $results = Get-BloatProcesses
        Show-BloatTable $results
        return $results
    }

    function Invoke-CleanWithConfirm {
        param(
            [System.Collections.Generic.List[PSCustomObject]]$Processes
        )

        if ($Processes.Count -eq 0) {
            Write-Host "  Nothing to clean — no bloat found above threshold." -ForegroundColor Green
            Write-Host ""
            return
        }

        # Calculate estimated impact
        $estMB = [math]::Round(($Processes | Measure-Object -Property MemMB -Sum).Sum, 1)

        while ($true) {
            Write-Host ""
            Write-Host "  Proceed with cleaning $($Processes.Count) process(es) (~$estMB MB)? (Y/N): " -NoNewline -ForegroundColor Yellow
            $confirm = Read-Host

            if ($confirm -match "^[Yy]$") {
                Invoke-Cleaner $Processes
                break
            }
            elseif ($confirm -match "^[Nn]$") {
                Write-Host "  Cancelled." -ForegroundColor DarkGray
                Write-Host ""
                break
            }
            else {
                Write-Host "  Invalid input. Enter Y or N." -ForegroundColor Red
            }
        }
    }

    # ============================================================
    #  MAIN LOOP
    # ============================================================

    Show-Header

    $lastScan = $null

    while ($true) {
        Show-Menu
        Write-Host "  > " -NoNewline -ForegroundColor Cyan
        $choice = Read-Host

        switch ($choice) {

            "1" {
                $lastScan = Invoke-ScanOnly
            }

            "2" {
                if ($null -eq $lastScan) {
                    Write-Host "  No scan yet — running scan first..." -ForegroundColor DarkGray
                    $lastScan = Invoke-ScanOnly
                }
                Invoke-CleanWithConfirm $lastScan
                $lastScan = $null
            }

            "3" {
                $lastScan = Invoke-ScanOnly
                Invoke-CleanWithConfirm $lastScan
                $lastScan = $null
                Show-RAMStats
            }

            "4" { Show-Help  }
            "5" { Show-About }

            "0" {
                Write-Host ""
                Write-Host "  Bye." -ForegroundColor DarkGray
                Write-Host ""
                break
            }

            default {
                Write-Host "  Invalid option. Enter 0-5." -ForegroundColor Red
                Write-Host ""
            }
        }

        if ($choice -eq "0") { break }
    }