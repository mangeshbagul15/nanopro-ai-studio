@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo  MANGESH NANO PRO AI STUDIO - HUGGING FACE CI/CD DEPLOY
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Git repository status...
git status --short

echo.
echo [2/4] Staging changes...
git add .

set COMMIT_MSG=NanoPro Production Sync - %date% %time%
echo [3/4] Creating local Git snapshot: "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"

echo.
echo [4/4] Pushing to Hugging Face Spaces (Cloud)...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS: NanoPro AI Studio deployed to Hugging Face!
    echo ========================================================
) else (
    echo.
    echo [!] Push failed or remote not configured yet.
    echo [!] Run: git remote add origin https://huggingface.co/spaces/<YOUR_USERNAME>/<YOUR_SPACE>
)

pause
