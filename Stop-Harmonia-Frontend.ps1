$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsDir = Join-Path $projectRoot "Logs"
$frontendPidFile = Join-Path $logsDir "harmonia_frontend.pid"
$frontendStdOut = Join-Path $logsDir "harmonia_frontend.out.log"
$frontendStdErr = Join-Path $logsDir "harmonia_frontend.err.log"

function Get-ManagedFrontendProcess
{
    if (-not (Test-Path -LiteralPath $frontendPidFile))
    {
        return $null
    }

    try
    {
        $managedProcessId = [int](Get-Content -LiteralPath $frontendPidFile -ErrorAction Stop | Select-Object -First 1)
        return Get-Process -Id $managedProcessId -ErrorAction Stop
    }
    catch
    {
        Remove-Item -LiteralPath $frontendPidFile -Force -ErrorAction SilentlyContinue
        return $null
    }
}

function Clear-ManagedFrontendLogs
{
    foreach ($logPath in @($frontendStdOut, $frontendStdErr))
    {
        if (Test-Path -LiteralPath $logPath)
        {
            Clear-Content -LiteralPath $logPath -ErrorAction SilentlyContinue
        }
    }
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
$managedFrontendProcess = Get-ManagedFrontendProcess
if ($managedFrontendProcess)
{
    Write-Host "Stopping Harmonia frontend (PID $($managedFrontendProcess.Id))..."
    & taskkill.exe /PID $managedFrontendProcess.Id /T /F | Out-Null
}
else
{
    Write-Host "No managed Harmonia frontend process was found."
}

Remove-Item -LiteralPath $frontendPidFile -Force -ErrorAction SilentlyContinue
Clear-ManagedFrontendLogs

Write-Host "Frontend shutdown complete."
