# PowerShell automation script to set up and run the project locally (non-interactive defaults)
# Usage: Right-click -> Run with PowerShell, or run in an elevated terminal.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# 1. Create virtual environment
if (-Not (Test-Path .\venv)) {
    python -m venv venv
}

# 2. Activate venv for this script session
& .\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure .env exists (use example as default)
if (-Not (Test-Path .env)) {
    Copy-Item .env.example .env -Force
}

# 5. Initialize database (SQLite by default)
python create_db.py

# 6. Start the Flask app
Start-Process -NoNewWindow -FilePath python -ArgumentList 'app.py'
Write-Host 'Flask app started. Open http://127.0.0.1:5000 in your browser.'
