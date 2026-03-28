@echo off
REM College Academic Management System - Startup Script for Windows

echo.
echo ========================================================
echo   College Academic Management System
echo   Role-Based Database Management
echo ========================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Display system information
echo.
echo ========================================================
echo   System Information
echo ========================================================
python -c "import sys; print(f'Python Version: {sys.version.split()[0]}')"
python -c "import fastapi; import sqlalchemy; print(f'FastAPI: {fastapi.__version__}')"
echo.

REM Start the FastAPI server
echo.
echo ========================================================
echo   Starting FastAPI Server
echo ========================================================
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Login page: http://127.0.0.1:8000/login
echo.
echo Demo Credentials:
echo   Admin: admin / adminpass
echo   HOD: hod / hodpass
echo   Faculty: fac1 / facpass
echo   Student: 1PV16CS001 / studpass
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the FastAPI app
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000

pause
