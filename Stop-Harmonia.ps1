$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsDir = Join-Path $projectRoot "Logs"
$backendPidFile = Join-Path $logsDir "harmonia_web.pid"
$backendStdOut = Join-Path $logsDir "harmonia_web.out.log"
$backendStdErr = Join-Path $logsDir "harmonia_web.err.log"

function Stop-WithError([string]$message)
{
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

function Get-ManagedBackendProcess
{
    if (-not (Test-Path -LiteralPath $backendPidFile))
    {
        return $null
    }

    try
    {
        $managedProcessId = [int](Get-Content -LiteralPath $backendPidFile -ErrorAction Stop | Select-Object -First 1)
        return Get-Process -Id $managedProcessId -ErrorAction Stop
    }
    catch
    {
        Remove-Item -LiteralPath $backendPidFile -Force -ErrorAction SilentlyContinue
        return $null
    }
}

function Clear-ManagedBackendLogs
{
    foreach ($logPath in @($backendStdOut, $backendStdErr))
    {
        if (Test-Path -LiteralPath $logPath)
        {
            Clear-Content -LiteralPath $logPath -ErrorAction SilentlyContinue
        }
    }
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$managedBackendProcess = Get-ManagedBackendProcess
if ($managedBackendProcess)
{
    Write-Host "Stopping Harmonia backend (PID $($managedBackendProcess.Id))..."
    Stop-Process -Id $managedBackendProcess.Id -Force -ErrorAction SilentlyContinue
}
else
{
    Write-Host "No managed Harmonia backend process was found."
}

Remove-Item -LiteralPath $backendPidFile -Force -ErrorAction SilentlyContinue
Clear-ManagedBackendLogs

Write-Host "Harmonia shutdown complete."
