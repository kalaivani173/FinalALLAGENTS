# ChangeIQ Backend Startup Script
# Run this script to start the FastAPI backend

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ChangeIQ NPCI AI Backend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$aicodePath = "$PSScriptRoot\aicode"
$envFile    = "$aicodePath\.env"
$venvPath   = "$aicodePath\.venv"

# ── Step 1: Find Python ──────────────────────────────────
Write-Host "[1/4] Locating Python..." -ForegroundColor Yellow

$python = $null

# Try refreshed PATH after winget install
$possiblePaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311-Embed\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe",
    "C:\Python311\python.exe",
    "C:\Python312\python.exe",
    "C:\Python310\python.exe",
    "$venvPath\Scripts\python.exe"
)

foreach ($p in $possiblePaths) {
    if (Test-Path $p) { $python = $p; break }
}

if (-not $python) {
    # Try from PATH (excluding WindowsApps stub)
    $found = Get-Command python -ErrorAction SilentlyContinue
    if ($found -and $found.Source -notlike '*WindowsApps*') {
        $python = $found.Source
    }
}

if (-not $python) {
    Write-Host "  Python not found. Installing via winget..." -ForegroundColor Red
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    Start-Sleep -Seconds 5
    # Reload PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    $found = Get-Command python -ErrorAction SilentlyContinue
    if ($found -and $found.Source -notlike '*WindowsApps*') {
        $python = $found.Source
    }
    foreach ($p in $possiblePaths) {
        if (Test-Path $p) { $python = $p; break }
    }
}

if (-not $python) {
    Write-Host "  ERROR: Could not find Python. Please install Python 3.11 from https://python.org" -ForegroundColor Red
    Write-Host "  Then re-run this script." -ForegroundColor Red
    Pause
    exit 1
}

Write-Host "  Found Python: $python" -ForegroundColor Green
& $python --version

# ── Step 2: Create venv if not present ──────────────────
Write-Host ""
Write-Host "[2/4] Setting up virtual environment..." -ForegroundColor Yellow

if (-not (Test-Path "$venvPath\Scripts\python.exe")) {
    Write-Host "  Creating .venv..." -ForegroundColor Gray
    & $python -m venv $venvPath
}

$venvPython = "$venvPath\Scripts\python.exe"
$venvPip    = "$venvPath\Scripts\pip.exe"
Write-Host "  Using venv: $venvPython" -ForegroundColor Green

# ── Step 3: Install requirements ─────────────────────────
Write-Host ""
Write-Host "[3/4] Installing Python packages..." -ForegroundColor Yellow
& $venvPip install --upgrade pip -q
& $venvPip install -r "$aicodePath\requirements.txt" -q
Write-Host "  Packages installed." -ForegroundColor Green

# ── Step 4: Check .env ───────────────────────────────────
Write-Host ""
Write-Host "[4/4] Checking .env configuration..." -ForegroundColor Yellow

if (-not (Test-Path $envFile)) {
    Copy-Item "$aicodePath\.env.example" $envFile
    Write-Host "  Created .env from template." -ForegroundColor Gray
}

$envContent = Get-Content $envFile -Raw
if ($envContent -match 'OPENAI_API_KEY=your-openai-api-key-here' -or $envContent -match 'OPENAI_API_KEY=$') {
    Write-Host ""
    Write-Host "  ⚠  OPENAI_API_KEY is not set in .env!" -ForegroundColor Yellow
    Write-Host "  Please edit: $envFile" -ForegroundColor Yellow
    Write-Host "  Set OPENAI_API_KEY=sk-xxxx..." -ForegroundColor Yellow
    Write-Host ""
    $key = Read-Host "  Enter your OpenAI API key now (or press Enter to skip)"
    if ($key -and $key.StartsWith("sk-")) {
        (Get-Content $envFile) -replace 'OPENAI_API_KEY=.*', "OPENAI_API_KEY=$key" | Set-Content $envFile
        Write-Host "  Key saved to .env" -ForegroundColor Green
    } else {
        Write-Host "  Skipped. AI spec generation will fail without a key." -ForegroundColor Yellow
    }
}

# ── Start the server ──────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting ChangeIQ Backend on :8000" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  API Base URL : http://localhost:8000" -ForegroundColor Green
Write-Host "  Chatbot UI   : http://localhost:5500" -ForegroundColor Green
Write-Host ""

Set-Location $aicodePath
& $venvPython -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
