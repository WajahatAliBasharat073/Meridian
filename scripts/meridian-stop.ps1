<#
.SYNOPSIS
  Stops Meridian's API and web servers.

.DESCRIPTION
  Stops by *port owner* first, then sweeps for known child processes.
  Both matter on Windows: `next dev` runs under a cmd.exe wrapper that
  spawns node children, and uvicorn's reloader spawns a worker whose command
  line contains no mention of uvicorn at all - kill the parent and the child
  keeps the port, which is the failure that makes later edits look like they
  never applied.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

function Stop-Port($Port, $Label) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { "$Label`: nothing listening on $Port"; return }
    foreach ($c in $conns) {
        $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
        "$Label`: stopping PID $($c.OwningProcess) ($($p.ProcessName)) on $Port"
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Stop-Port 8199 'api'
Stop-Port 3001 'web'

# Sweep orphans that survived losing their parent.
$patterns = @(
    "*uvicorn*app.main*",
    "*$Root\web*next*dev*",
    "*multiprocessing-fork*"
)
$killed = 0
foreach ($proc in Get-CimInstance Win32_Process) {
    if (-not $proc.CommandLine) { continue }
    if ($proc.ProcessId -eq $PID) { continue }
    foreach ($pat in $patterns) {
        if ($proc.CommandLine -like $pat) {
            # Don't match this script's own shell.
            if ($proc.CommandLine -like '*meridian-stop*') { break }
            "sweep: stopping PID $($proc.ProcessId) ($($proc.Name))"
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
            $killed++
            break
        }
    }
}
if ($killed -eq 0) { 'sweep: no orphans' }

Start-Sleep -Seconds 2
foreach ($p in 8199, 3001) {
    $still = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($still) { "WARNING: port $p still held by PID $($still.OwningProcess)" } else { "port $p : free" }
}
