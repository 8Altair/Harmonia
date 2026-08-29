$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendRoot = Join-Path $projectRoot "frontend"
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$logsDir = Join-Path $projectRoot "Logs"
$frontendBuildEntry = Join-Path $projectRoot "static\app\index.html"
$backendStdOut = Join-Path $logsDir "harmonia_web.out.log"
$backendStdErr = Join-Path $logsDir "harmonia_web.err.log"
$backendPidFile = Join-Path $logsDir "harmonia_web.pid"
$appUrl = "http://127.0.0.1:5000"

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

function Test-UrlReady([string]$url) {
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
        if ([string]::IsNullOrWhiteSpace($candidatePath))
        {
            continue
        }

        if (Test-Path -LiteralPath $candidatePath)
        {
            return $candidatePath
        }
    }

    return $null
}

function Wait-ForUrl([string]$url, [int]$timeoutSeconds = 180)
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

function Get-ManagedBackendProcess
{
    if (-not (Test-Path $backendPidFile))
    {
        return $null
    }

    try
    {
        $managedProcessId = [int](Get-Content $backendPidFile -ErrorAction Stop | Select-Object -First 1)
        return Get-Process -Id $managedProcessId -ErrorAction Stop
    }
    catch
    {
        Remove-Item $backendPidFile -Force -ErrorAction SilentlyContinue
        return $null
    }
}

function Invoke-FrontendBuild
{
    $nodeExe = Resolve-NodeToolPath "node.exe"
    $npmCmd = Resolve-NodeToolPath "npm.cmd"

    if (-not (Test-Path $frontendRoot))
    {
        Stop-WithError "The frontend directory was not found at $frontendRoot."
    }

    if (-not $nodeExe -or -not $npmCmd)
    {
        Stop-WithError "Node.js and npm are not available. Install Node.js or configure the PyCharm-managed runtime before running Harmonia."
    }

    $nodeBinDir = Split-Path -Parent $nodeExe
    $originalPath = $env:Path

    Push-Location $frontendRoot
    try
    {
        if ($nodeBinDir)
        {
            $env:Path = "$nodeBinDir;$originalPath"
        }

        if (-not (Test-Path (Join-Path $frontendRoot "node_modules")))
        {
            Write-Host "Installing frontend dependencies..."
            & $npmCmd install
            if ($LASTEXITCODE -ne 0)
            {
                Stop-WithError "npm install failed."
            }
        }

        Write-Host "Building frontend..."
        & $npmCmd run build
        if ($LASTEXITCODE -ne 0)
        {
            Stop-WithError "npm run build failed."
        }
    }
    finally
    {
        $env:Path = $originalPath
        Pop-Location
    }

    if (-not (Test-Path $frontendBuildEntry))
    {
        Stop-WithError "Frontend build did not produce $frontendBuildEntry."
    }
}

function Start-Backend
{
    if (-not (Test-Path $pythonExe))
    {
        Stop-WithError "The virtual environment Python executable was not found at $pythonExe."
    }

    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Clear-Content $backendStdOut -ErrorAction SilentlyContinue
    Clear-Content $backendStdErr -ErrorAction SilentlyContinue

    Write-Host "Starting Flask backend..."
    $process = Start-Process `
        -FilePath $pythonExe `
        -ArgumentList "app.py" `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $backendStdOut `
        -RedirectStandardError $backendStdErr `
        -PassThru

    Set-Content -Path $backendPidFile -Value $process.Id

    if (-not (Wait-ForUrl -url $appUrl))
    {
        $errorTail = ""
        if (Test-Path $backendStdErr)
        {
            $errorTail = (Get-Content $backendStdErr -Tail 40 -ErrorAction SilentlyContinue) -join [Environment]::NewLine
        }

        Stop-WithError "The Flask server did not become ready at $appUrl.`n`nRecent backend log output:`n$errorTail"
    }
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$managedBackendProcess = Get-ManagedBackendProcess
if ($managedBackendProcess -and -not (Test-UrlReady -url $appUrl))
{
    Stop-Process -Id $managedBackendProcess.Id -Force -ErrorAction SilentlyContinue
    Remove-Item $backendPidFile -Force -ErrorAction SilentlyContinue
    $managedBackendProcess = $null
}

if (Test-PortListening -port 5000)
{
    if (Test-UrlReady -url $appUrl)
    {
        Write-Host "Harmonia is already running. Opening the website..."
        Start-Process $appUrl
        exit 0
    }

    Stop-WithError "Port 5000 is already in use by another process."
}

Invoke-FrontendBuild
Start-Backend

Write-Host "Opening Harmonia at $appUrl"
Start-Process $appUrl
