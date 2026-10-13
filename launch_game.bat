@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting Zombi Apploclips Mobile FPS Engine...
echo ===================================================
python main.py
if errorlevel 1 (
    echo.
    echo Game exited with error code %errorlevel%
    pause
)
