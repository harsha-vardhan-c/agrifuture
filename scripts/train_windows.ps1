# Run only when retraining or after updating the price dataset.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Error 'Create the virtual environment first: py -m venv .venv'
}
& '.\.venv\Scripts\python.exe' -m backend.train
