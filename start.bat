@echo off
echo ==========================================
echo Starting Automated Insight Engine
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo + Python found

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo + Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo + Virtual environment activated

REM Install dependencies from backend folder
echo.
echo Installing dependencies...
pip install -q -r backend\requirements.txt
echo + Dependencies installed

REM Create necessary directories
echo.
echo Creating directories...
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist outputs\charts mkdir outputs\charts
echo + Directories created

REM Check if config.py exists in backend
if not exist backend\config.py (
    echo.
    echo ⚠️  Warning: backend\config.py not found!
    echo Please copy config.example.py to config.py and add your API key
    pause
    exit /b 1
)

echo.
echo ==========================================
echo + Setup complete!
echo ==========================================
echo.
echo Starting Backend Server...
echo ==========================================
echo Backend will run on: http://localhost:5000
echo Frontend: Open frontend\index.html in your browser
echo.
echo To stop the server, press Ctrl+C
echo.

REM Change to backend directory and run
cd backend
python app.py