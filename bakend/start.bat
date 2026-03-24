@echo off
REM VideoQA Backend – Windows Startup Script
REM Run this from the backend\ directory

echo.
echo ============================================
echo   VideoQA Backend – Starting up
echo ============================================
echo.

REM Check if venv exists, create if not
if not exist "venv" (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
)

REM Activate venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting server at http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop.
echo.

python main.py
