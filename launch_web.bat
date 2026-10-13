@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Zombi Apploclips Web App Server...
echo ========================================================
echo Serving on http://localhost:8080/webapp/
start http://localhost:8080/webapp/
python -m http.server 8080
if errorlevel 1 (
    echo.
    echo Server stopped.
    pause
)
