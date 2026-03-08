@echo off
title Church Bible Presentation System
color 0A
cls

echo.
echo  =====================================================
echo       CHURCH BIBLE VERSE PRESENTATION SYSTEM
echo  =====================================================
echo.

:: Check Python
echo  [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed!
    echo  Download from: https://www.python.org/downloads/
    echo  IMPORTANT: Tick "Add Python to PATH" during install!
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b
)
python --version
echo  Python found!

:: Install dependencies
echo.
echo  [2/5] Installing required packages (first time takes a few minutes)...
pip install flask flask-cors openai-whisper sounddevice scipy numpy --quiet
echo  Packages ready!

:: Initialize database
echo.
echo  [3/5] Setting up Bible database...
if not exist "database\bible.db" (
    python database\seed.py
) else (
    echo  Database already exists - skipping
)

:: Find local IP
echo.
echo  [4/5] Finding your network address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set MYIP=%%a
    goto :found_ip
)
:found_ip
set MYIP=%MYIP: =%

echo  Your local IP: %MYIP%

:: Launch
echo.
echo  [5/5] Launching server...
echo.
echo  ====================================================
echo   SYSTEM IS RUNNING - DO NOT CLOSE THIS WINDOW
echo  ====================================================
echo.
echo   YOUR COMPUTER:
echo   Control Panel  -- http://localhost:5000
echo   Display Screen -- http://localhost:5000/display
echo.
echo   FROM PROJECTOR PC / ANOTHER DEVICE:
echo   http://%MYIP%:5000/display
echo.
echo  ====================================================
echo.

timeout /t 3 /nobreak >nul
start http://localhost:5000
start http://localhost:5000/display

python backend\app.py

echo.
echo  Server stopped. Press any key to exit.
pause
