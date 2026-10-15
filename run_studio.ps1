Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "               MANGESH NANO PRO AI STUDIO" -ForegroundColor Green
Write-Host "       Enterprise Autonomous Multi-Agent Operations & Database Hub" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

# Stop any lingering process on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "[*] Terminating previous process on port 8000 (PID: $($_.OwningProcess))..." -ForegroundColor Yellow
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

$pythonCmd = "python"
if (Test-Path "venv\Scripts\python.exe") {
    $pythonCmd = "venv\Scripts\python.exe"
} elseif (Test-Path "..\venv\Scripts\python.exe") {
    $pythonCmd = "..\venv\Scripts\python.exe"
} elseif (Test-Path "C:\Mangesh\AI video\venv\Scripts\python.exe") {
    $pythonCmd = "C:\Mangesh\AI video\venv\Scripts\python.exe"
}

Write-Host "[*] Launching Mangesh Nano Pro AI Studio with $pythonCmd..." -ForegroundColor Yellow
& $pythonCmd main.py
