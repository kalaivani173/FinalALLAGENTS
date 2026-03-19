@echo off
title ChangeIQ Backend Starter
color 0B

echo.
echo  ============================================
echo   ChangeIQ NPCI - Full Stack Startup
echo  ============================================
echo.

set AICODE=%~dp0aicode
set VENV=%AICODE%\.venv
set EMBEDPYTHON=%LOCALAPPDATA%\Programs\Python\Python311-Embed\python.exe

:: ── Step 1: Find Python ──────────────────────────────────────────────
set PYTHON=

:: Check embeddable Python first (installed by this project)
if exist "%EMBEDPYTHON%" (
  set PYTHON=%EMBEDPYTHON%
  goto :found_python
)

:: Check standard installs
for %%p in (
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
  "C:\Python311\python.exe"
  "C:\Python312\python.exe"
) do (
  if exist %%p (
    set PYTHON=%%p
    goto :found_python
  )
)

:: Try from PATH
for /f "delims=" %%i in ('where python 2^>nul ^| findstr /v "WindowsApps"') do (
  set PYTHON=%%i
  goto :found_python
)

echo  [!] Python not found. Installing portable Python (no admin needed)...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "[Net.ServicePointManager]::SecurityProtocol='Tls12';" ^
  "$d='%LOCALAPPDATA%\Programs\Python\Python311-Embed';" ^
  "New-Item -ItemType Directory -Path $d -Force | Out-Null;" ^
  "Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%TEMP%\py_embed.zip' -UseBasicParsing;" ^
  "Expand-Archive '%TEMP%\py_embed.zip' -DestinationPath $d -Force;" ^
  "$pth=Join-Path $d 'python311._pth';" ^
  "(Get-Content $pth) -replace '#import site','import site' | Set-Content $pth;" ^
  "Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' -UseBasicParsing;" ^
  "& \"$d\python.exe\" '%TEMP%\get-pip.py' --no-warn-script-location"
if exist "%EMBEDPYTHON%" (
  set PYTHON=%EMBEDPYTHON%
  goto :found_python
)

echo  [!] Could not install Python. Please install Python 3.11 from https://python.org
pause
exit /b 1

:found_python
echo  [OK] Python: %PYTHON%
%PYTHON% --version
echo.

:: ── Step 2: Install virtualenv + create venv ────────────────────────
if not exist "%VENV%\Scripts\python.exe" (
  echo  [*] Setting up virtual environment...
  %PYTHON% -m pip install virtualenv -q
  %PYTHON% -m virtualenv "%VENV%" -q
  echo  [OK] Virtual environment created.
)

set VPYTHON=%VENV%\Scripts\python.exe
set VPIP=%VENV%\Scripts\pip.exe

:: ── Step 3: Install requirements ────────────────────────────────────
echo  [*] Installing/checking Python packages...
"%VPIP%" install --upgrade pip -q
"%VPIP%" install python-multipart -q
"%VPIP%" install -r "%AICODE%\requirements.txt" -q
echo  [OK] Packages ready.
echo.

:: ── Step 4: Check OpenAI key ─────────────────────────────────────────
findstr /c:"OPENAI_API_KEY=your-openai-api-key-here" "%AICODE%\.env" >nul 2>&1
if %errorlevel%==0 (
  echo  [!] WARNING: OPENAI_API_KEY is not set in .env
  echo      Edit: %AICODE%\.env
  echo      Set: OPENAI_API_KEY=sk-xxxx...
  echo.
  set /p APIKEY= Enter your OpenAI API key (or press Enter to skip):
  if not "%APIKEY%"=="" (
    powershell -Command "(Get-Content '%AICODE%\.env') -replace 'OPENAI_API_KEY=.*', 'OPENAI_API_KEY=%APIKEY%' | Set-Content '%AICODE%\.env'"
    echo  [OK] API key saved.
  )
  echo.
)

:: ── Step 5: Start chatbot UI server on port 5500 ────────────────────
echo  [*] Starting Chatbot UI on http://localhost:5500 ...
start "ChangeIQ UI Server" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0chatbot-ui\serve.ps1"
timeout /t 2 >nul

:: ── Step 6: Start FastAPI backend ───────────────────────────────────
echo.
echo  ============================================
echo   Starting FastAPI Backend on port 8000
echo   Chatbot UI  : http://localhost:5500
echo   API Docs    : http://localhost:8000/docs
echo  ============================================
echo.

cd /d "%AICODE%"
"%VPYTHON%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
