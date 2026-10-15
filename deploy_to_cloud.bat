@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo  MANGESH NANO PRO AI STUDIO - GITHUB & CLOUD CI/CD DEPLOY
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
echo [4/4] Pushing to GitHub (Cloud Auto-Deploy)...
git push https://mangeshbagul15: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@github.com/mangeshbagul15/nanopro-ai-studio.git main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS: NanoPro AI Studio synchronized to GitHub!
    echo ========================================================
) else (
    echo.
    echo [!] Push failed. Check your network connection.
)

pause
