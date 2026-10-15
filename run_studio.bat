@echo off
TITLE Mangesh Nano Pro AI Operating Center - Autonomous Operations Manager
COLOR 0B
echo ===============================================================================
echo                MANGESH NANO PRO AI OPERATING CENTER
echo        Enterprise Autonomous Multi-Agent Operations & Database Hub
echo ===============================================================================
echo.

REM Determine current directory
cd /d "%~dp0"

REM Free port 8000 if occupied by previous session
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo [*] Terminating previous background instance on port 8000 (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

REM Auto-sync latest cloud updates from GitHub before starting
echo [*] Checking and auto-syncing with Cloud / GitHub...
git pull origin main >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [*] Cloud Auto-Sync: Local codebase is 100%% up to date!
)

REM Find python in venv or system path
set PYTHON_CMD=python
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    echo [*] Detected virtual environment at venv
) else if exist "..\venv\Scripts\python.exe" (
    set PYTHON_CMD=..\venv\Scripts\python.exe
    echo [*] Detected virtual environment at ..\venv
) else if exist "C:\Mangesh\AI video\venv\Scripts\python.exe" (
    set PYTHON_CMD="C:\Mangesh\AI video\venv\Scripts\python.exe"
    echo [*] Detected virtual environment at C:\Mangesh\AI video\venv
)

echo [*] Starting Mangesh Nano Pro AI Operating Center with %PYTHON_CMD%...
echo [*] Server binding to http://127.0.0.1:8000
echo [*] Google Chrome will launch automatically.
echo.
%PYTHON_CMD% main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server exited with code %ERRORLEVEL%.
    pause
)
