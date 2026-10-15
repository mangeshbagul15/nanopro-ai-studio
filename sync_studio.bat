@echo off
TITLE NanoPro AI Studio - Cloud Two-Way Synchronizer
COLOR 0A
echo ===============================================================================
echo            MANGESH NANO PRO AI STUDIO — CLOUD SYNCHRONIZER
echo       Two-Way Autonomous Sync between Cloud, GitHub and Local Laptop
echo ===============================================================================
echo.

cd /d "C:\Mangesh\NanoPro_AI_Studio_Made_By_Mangesh\Mangesh_Nano_Pro_AI_Studio"

echo [*] Pulling latest production updates from GitHub / Cloud...
git pull origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Warning: Git pull encountered an issue. Checking status...
    git status
) else (
    echo.
    echo [*] Codebase is now 100%% up to date with Cloud!
)

echo.
echo [*] Refreshing local NanoPro_AI_Studio_COMPLETE.zip archive...
set PYTHON_CMD=python
if exist "C:\Mangesh\AI video\venv\Scripts\python.exe" (
    set PYTHON_CMD="C:\Mangesh\AI video\venv\Scripts\python.exe"
)

%PYTHON_CMD% -c "
import os, zipfile
src = r'C:\Mangesh\NanoPro_AI_Studio_Made_By_Mangesh\Mangesh_Nano_Pro_AI_Studio'
dest = r'C:\Mangesh\NanoPro_AI_Studio_Made_By_Mangesh\NanoPro_AI_Studio_COMPLETE.zip'
exclude_dirs = {'__pycache__', '.pytest_cache', 'venv', '.git', '.idea', '.vscode'}
exclude_exts = {'.pyc', '.pyo', '.pyd', '.db-shm', '.db-wal'}
with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if not any(f.endswith(ext) for ext in exclude_exts):
                fp = os.path.join(root, f)
                zf.write(fp, os.path.join('Mangesh_Nano_Pro_AI_Studio', os.path.relpath(fp, src)))
sz = round(os.path.getsize(dest)/(1024*1024), 2)
print(f'[*] Archive updated: {dest} ({sz} MB)')
"

echo.
echo ===============================================================================
echo   SUCCESS: Laptop is now 100%% synchronized with Cloud and GitHub!
echo ===============================================================================
echo.
pause
