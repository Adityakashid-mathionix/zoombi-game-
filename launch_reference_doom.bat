@echo off
cd /d "%~dp0reference_doom"
echo ===================================================
echo Starting Reference DOOM Engine (Multi-level)...
echo ===================================================
python main.py
if errorlevel 1 (
    echo.
    echo Game exited with error code %errorlevel%
    pause
)
