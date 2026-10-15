@echo off
echo ========================================================
echo  MANGESH NANO PRO AI STUDIO - INSTANT ROLLBACK SAFETY
echo ========================================================
echo.
echo WARNING: This will rollback all files to the last stable checkpoint (v7-STABLE).
set /p CONFIRM="Are you sure you want to rollback? (Y/N): "
if /i "%CONFIRM%" neq "Y" (
    echo Rollback cancelled.
    pause
    exit /b
)

cd /d "%~dp0"
git reset --hard v7-STABLE
echo.
echo [OK] Successfully restored to v7-STABLE baseline!
pause
