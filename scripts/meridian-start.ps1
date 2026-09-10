<#
.SYNOPSIS
  Starts Meridian's API and web servers, hidden, and waits until both answer.

.DESCRIPTION
  Run automatically at logon by the "Meridian Autostart" scheduled task, and
  safe to run by hand at any time: it is idempotent. If a server is already
  healthy it is left alone; if a dead process is still holding a port, that
  process is cleared first.

  Two details this script exists to get right:

  * Working directories. api/app/config.py reads `env_file=".env"`, which is
    resolved relative to the *current directory*. Start the API from the
    wrong place and it silently falls back to its defaults - which means an
    empty SUPABASE_URL, which means app/deps.py stops verifying tokens and
    serves the dev stub user instead. The app would appear to work while
    showing the wrong account's data. So each server is started with an
    explicit -WorkingDirectory, and the check below catches it if that ever
    breaks.

  * Ports before processes. Killing a reloader parent on Windows can leave
    its worker alive still holding the port, so stale listeners are cleared
    by port owner rather than by process name.
#>
[CmdletBinding()]
param(
    # Skip the wait-and-verify phase. Only useful for a fire-and-forget call.
    [switch]$NoWait
)

$ErrorActionPreference = 'Stop'

$Root    = Split-Path -Parent $PSScriptRoot
$ApiDir  = Join-Path $Root 'api'
$WebDir  = Join-Path $Root 'web'
$LogDir  = Join-Path $Root 'logs'
$ApiPort = 8199
$WebPort = 3001

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$RunLog = Join-Path $LogDir 'autostart.log'

function Write-Log($Message) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Write-Host $line
    Add-Content -Path $RunLog -Value $line -Encoding utf8
}

function Test-Port($Port) {
    $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Test-Http($Url, $TimeoutSec = 4) {
    try {
        $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        return [int]$r.StatusCode
    } catch {
        # A 4xx still means something is listening and answering.
        if ($_.Exception.Response) { return [int]$_.Exception.Response.StatusCode }
        return 0
    }
}

function Clear-StalePort($Port, $Label) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        Write-Log "$Label`: clearing stale listener on $Port (PID $($c.OwningProcess))"
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    if ($conns) { Start-Sleep -Seconds 2 }
}

Write-Log '--- Meridian autostart ---'

# ----------------------------------------------------------------- API ----
if ((Test-Http "http://localhost:$ApiPort/health") -eq 200) {
    Write-Log "api  : already healthy on $ApiPort, leaving it alone"
} else {
    Clear-StalePort $ApiPort 'api'
    $py = Join-Path $ApiDir '.venv\Scripts\python.exe'
    if (-not (Test-Path $py)) { Write-Log "api  : FATAL - no venv at $py"; exit 1 }

    Write-Log "api  : starting on $ApiPort"
    Start-Process -FilePath $py `
        -ArgumentList '-m', 'uvicorn', 'app.main:app', '--port', "$ApiPort" `
        -WorkingDirectory $ApiDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir 'api.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'api.err.log')
}

# ----------------------------------------------------------------- web ----
if ((Test-Http "http://localhost:$WebPort/login" 6) -ne 0) {
    Write-Log "web  : already answering on $WebPort, leaving it alone"
} else {
    Clear-StalePort $WebPort 'web'
    $next = Join-Path $WebDir 'node_modules\.bin\next.cmd'
    if (-not (Test-Path $next)) { Write-Log "web  : FATAL - next not installed at $next"; exit 1 }

    Write-Log "web  : starting on $WebPort"
    Start-Process -FilePath 'cmd.exe' `
        -ArgumentList '/c', "`"$next`" dev -p $WebPort" `
        -WorkingDirectory $WebDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir 'web.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'web.err.log')
}

if ($NoWait) { Write-Log 'launched (not waiting)'; exit 0 }

# ------------------------------------------------------------- verify -----
# Next's first compile is slow on a cold start, so the web budget is
# generous. The API should be up in a couple of seconds.
$apiOk = $false
$webOk = $false
for ($i = 1; $i -le 40; $i++) {
    if (-not $apiOk) { $apiOk = (Test-Http "http://localhost:$ApiPort/health") -eq 200 }
    if (-not $webOk) { $webOk = (Test-Http "http://localhost:$WebPort/login" 6) -eq 200 }
    if ($apiOk -and $webOk) { break }
    Start-Sleep -Seconds 3
}

Write-Log ("api  : {0}" -f $(if ($apiOk) { "healthy on $ApiPort" } else { "NOT RESPONDING - see logs\api.err.log" }))
Write-Log ("web  : {0}" -f $(if ($webOk) { "serving on $WebPort" } else { "NOT RESPONDING - see logs\web.err.log" }))

if ($apiOk) {
    # Canary for the working-directory problem described at the top. With
    # .env loaded, an unauthenticated request must be refused. A 200 here
    # means the API is running in stub-user mode and is about to show the
    # wrong person's data.
    $code = Test-Http "http://localhost:$ApiPort/api/today"
    if ($code -eq 401) {
        Write-Log 'auth : OK (.env loaded, tokens verified)'
    } elseif ($code -eq 200) {
        Write-Log 'auth : WARNING - /api/today answered without a token. api/.env was not loaded, so the API is serving the dev stub user rather than your account. Check the working directory.'
    } else {
        Write-Log "auth : unexpected status $code from /api/today"
    }
}

if ($apiOk -and $webOk) {
    Write-Log "ready: http://localhost:$WebPort"
    exit 0
}
exit 1
