# Run from the project root in PowerShell:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -m venv .venv
}

& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }

Write-Host ''
Write-Host 'Starting AgriForecast at http://127.0.0.1:8000' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop the server.'
& '.\.venv\Scripts\python.exe' -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
