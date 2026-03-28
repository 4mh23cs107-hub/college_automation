#!/usr/bin/env pwsh
# College Academic Management System - Startup Script for PowerShell

Write-Host ""
Write-Host "========================================================"
Write-Host "   College Academic Management System" -ForegroundColor Cyan
Write-Host "   Role-Based Database Management" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Display system information
Write-Host ""
Write-Host "========================================================"
Write-Host "   System Information" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
python -c "import sys; print(f'Python Version: {sys.version.split()[0]}')"
python -c "import fastapi; print(f'FastAPI Version: {fastapi.__version__}')"
Write-Host ""

# Start the FastAPI server
Write-Host "========================================================"
Write-Host "   Starting FastAPI Server" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Login page: http://127.0.0.1:8000/login" -ForegroundColor Green
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Yellow
Write-Host "   Admin: admin / adminpass" -ForegroundColor White
Write-Host "   HOD: hod / hodpass" -ForegroundColor White
Write-Host "   Faculty: fac1 / facpass" -ForegroundColor White
Write-Host "   Student: 1PV16CS001 / studpass" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the FastAPI app
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
