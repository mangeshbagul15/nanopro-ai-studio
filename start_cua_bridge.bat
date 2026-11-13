@echo off
setlocal
cd /d "%~dp0"
title NanoPro CUA Bridge - real Chromium for the AI agent
color 0B

echo =======================================================================
echo        NANOPRO CUA BRIDGE - real browser for the Global AI Lab
echo =======================================================================
echo.
echo [1/3] Checking Python packages (playwright, aiohttp)...
python -m pip install --quiet --disable-pip-version-check playwright aiohttp python-dotenv
if errorlevel 1 (
    echo [ERROR] pip install failed. Make sure Python is on PATH.
    pause
    exit /b 1
)

echo [2/3] Checking the Chromium binary...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Could not install Chromium.
    pause
    exit /b 1
)

echo [3/3] Starting the bridge on http://127.0.0.1:8765 ...
echo.
echo  A Chromium window will open. Keep BOTH windows running while the
echo  agent works - closing them stops the agent.
echo.
echo  The agent can click, type, scroll, select, copy, paste, drag,
echo  download (saved to %%USERPROFILE%%\Downloads\NanoProCUA) and upload
echo  local files. Everything runs on THIS laptop, not on Render.
echo.
python app\agents\local_cua_bridge.py --headed
echo.
echo Bridge stopped.
pause
