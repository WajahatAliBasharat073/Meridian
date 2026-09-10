<#
.SYNOPSIS
  Registers (or removes) the scheduled task that starts Meridian at logon.

.DESCRIPTION
  Runs as the current user at logon - no admin rights, no stored password,
  nothing running while you are logged out.

  Why Task Scheduler rather than a Startup-folder shortcut: a shortcut gives
  no delay, no retry, and no way to see whether it ran. This gives a delay
  so the network is up before the API tries Supabase, a restart if the
  launcher fails, and a run history in Task Scheduler.

  Usage:
    powershell -ExecutionPolicy Bypass -File scripts\install-autostart.ps1
    powershell -ExecutionPolicy Bypass -File scripts\install-autostart.ps1 -Remove
#>
[CmdletBinding()]
param(
    [switch]$Remove,
    # Time to wait after logon before starting. The API talks to Supabase on
    # its first request, so it is worth letting the network settle.
    [string]$Delay = 'PT45S'
)

$ErrorActionPreference = 'Stop'

$TaskName = 'Meridian Autostart'
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $PSScriptRoot 'meridian-start.ps1'

if ($Remove) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        "Removed scheduled task '$TaskName'. Meridian will no longer start at logon."
    } else {
        "No scheduled task named '$TaskName' - nothing to remove."
    }
    return
}

if (-not (Test-Path $Script)) { throw "Launcher not found at $Script" }

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Script`"" `
    -WorkingDirectory $Root

$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$trigger.Delay = $Delay

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -DontStopOnIdleEnd `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description 'Starts the Meridian API (8199) and web (3001) dev servers at logon, hidden. See scripts\meridian-start.ps1.' `
    -Force | Out-Null

"Registered '$TaskName'."
"  runs   : at logon, $Delay after, hidden, as $env:USERNAME"
"  script : $Script"
"  logs   : $(Join-Path $Root 'logs')"
""
"Start it now without rebooting:   Start-ScheduledTask -TaskName '$TaskName'"
"Turn it off:                      scripts\install-autostart.ps1 -Remove"
