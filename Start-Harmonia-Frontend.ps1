$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendRoot = Join-Path $projectRoot "frontend"
$logsDir = Join-Path $projectRoot "Logs"
$frontendStdOut = Join-Path $logsDir "harmonia_frontend.out.log"
$frontendStdErr = Join-Path $logsDir "harmonia_frontend.err.log"
$frontendPidFile = Join-Path $logsDir "harmonia_frontend.pid"
$frontendUrl = "http://127.0.0.1:5173"

function Stop-WithError([string]$message)
{
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

function Test-PortListening([int]$port)
{
    try
    {
        $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop | Select-Object -First 1
        return $null -ne $connection
    }
    catch
    {
        return $false
    }
}

function Test-UrlReady([string]$url)
{
    try
    {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch
    {
        return $false
    }
}

function Resolve-NodeToolPath([string]$toolName)
{
    $command = Get-Command $toolName -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command)
    {
        return $command.Source
    }

    $candidatePaths = New-Object System.Collections.Generic.List[string]
    if ($env:LOCALAPPDATA)
    {
        $nodeProgramsRoot = Join-Path $env:LOCALAPPDATA "Programs\nodejs"
        $candidatePaths.Add((Join-Path $nodeProgramsRoot $toolName))

        $jetBrainsRoot = Join-Path $env:LOCALAPPDATA "JetBrains"
        try
        {
            $pyCharmRoots = Get-ChildItem -LiteralPath $jetBrainsRoot -Directory -Filter "PyCharm*" -ErrorAction Stop |
                Sort-Object Name -Descending
            foreach ($pyCharmRoot in $pyCharmRoots)
            {
                $runtimeRoot = Join-Path $pyCharmRoot.FullName "acp-agents\.runtimes\node"
                $candidatePaths.Add((Join-Path $runtimeRoot $toolName))

                $runtimeVersions = Get-ChildItem -LiteralPath $runtimeRoot -Directory -ErrorAction SilentlyContinue |
                    Sort-Object Name -Descending
                foreach ($runtimeVersion in $runtimeVersions)
                {
                    $candidatePaths.Add((Join-Path $runtimeVersion.FullName $toolName))
                }
            }
        }
        catch
        {
        }
    }

    foreach ($candidatePath in $candidatePaths)
    {
        if ($candidatePath -and (Test-Path -LiteralPath $candidatePath))
        {
            return $candidatePath
        }
    }

    return $null
}

function Wait-ForUrl([string]$url, [int]$timeoutSeconds = 60)
{
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    while ($stopwatch.Elapsed.TotalSeconds -lt $timeoutSeconds)
    {
        if (Test-UrlReady -url $url)
        {
            return $true
        }

        Start-Sleep -Seconds 2
    }

    return $false
}

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

function Stop-ManagedFrontendProcess([System.Diagnostics.Process]$process)
{
    & taskkill.exe /PID $process.Id /T /F | Out-Null
    Remove-Item -LiteralPath $frontendPidFile -Force -ErrorAction SilentlyContinue
}

function Get-LogTail
{
    if (-not (Test-Path -LiteralPath $frontendStdErr))
    {
        return ""
    }

    return (Get-Content -LiteralPath $frontendStdErr -Tail 40 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
}

if (-not (Test-Path -LiteralPath $frontendRoot))
{
    Stop-WithError "The frontend directory was not found at $frontendRoot."
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
$managedFrontendProcess = Get-ManagedFrontendProcess

if ($managedFrontendProcess -and (Test-UrlReady -url $frontendUrl))
{
    Write-Host "The Harmonia frontend is already running. Opening the website..."
    Start-Process $frontendUrl
    exit 0
}

if ($managedFrontendProcess)
{
    Stop-ManagedFrontendProcess -process $managedFrontendProcess
}

if (Test-PortListening -port 5173)
{
    Stop-WithError "Port 5173 is already in use by another process."
}

$nodeExe = Resolve-NodeToolPath "node.exe"
$npmCmd = Resolve-NodeToolPath "npm.cmd"
if (-not $nodeExe -or -not $npmCmd)
{
    Stop-WithError "Node.js and npm are not available. Install Node.js or configure the PyCharm-managed runtime before starting the frontend."
}

$nodeBinDir = Split-Path -Parent $nodeExe
$originalPath = $env:Path
$originalPreviewMode = $env:VITE_FRONTEND_ONLY
try
{
    $env:Path = "$nodeBinDir;$originalPath"
    $env:VITE_FRONTEND_ONLY = "true"
    if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot "node_modules")))
    {
        Write-Host "Installing frontend dependencies..."
        Push-Location $frontendRoot
        try
        {
            & $npmCmd install
            if ($LASTEXITCODE -ne 0)
            {
                Stop-WithError "npm install failed."
            }
        }
        finally
        {
            Pop-Location
        }
    }

    Clear-Content -LiteralPath $frontendStdOut -ErrorAction SilentlyContinue
    Clear-Content -LiteralPath $frontendStdErr -ErrorAction SilentlyContinue
    Write-Host "Starting Harmonia frontend..."
    $process = Start-Process `
        -FilePath $npmCmd `
        -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort") `
        -WorkingDirectory $frontendRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $frontendStdOut `
        -RedirectStandardError $frontendStdErr `
        -PassThru
}
finally
{
    $env:Path = $originalPath
    if ($null -eq $originalPreviewMode)
    {
        Remove-Item Env:VITE_FRONTEND_ONLY -ErrorAction SilentlyContinue
    }
    else
    {
        $env:VITE_FRONTEND_ONLY = $originalPreviewMode
    }
}

Set-Content -LiteralPath $frontendPidFile -Value $process.Id
if (-not (Wait-ForUrl -url $frontendUrl))
{
    Stop-ManagedFrontendProcess -process $process
    Stop-WithError "The frontend did not become ready at $frontendUrl.`n`nRecent frontend log output:`n$(Get-LogTail)"
}

Write-Host "Opening Harmonia frontend at $frontendUrl"
Start-Process $frontendUrl
