@echo off
TITLE Edu & Skill Path Recommender Launcher
echo ========================================
echo Edu & Skill Path Recommender
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo Error: Cannot find manage.py
    echo Please run this script from the project root directory
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo.
)

REM Run the launcher script
echo Starting the application...
python launcher.py --setup

echo.
echo Application closed.
pause