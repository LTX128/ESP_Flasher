@echo off
title ESP Flasher Pro Setup - Made by LTX
color D
cls

ping -n 2 127.0.0.1 >nul

echo =======================
echo     Only for ESP !!!
echo =======================
echo.

ping -n 3 127.0.0.1 >nul

cls

echo ==================================
echo         ESP Flasher Pro
echo            Setup
echo            by LTX
echo ==================================
echo.

echo Checking Python...

ping -n 3 127.0.0.1 >nul

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed.
    echo Install Python and restart setup.
    echo.
    pause
    exit
)

echo.
echo Python detected.

echo.

echo Installing requirements...

ping -n 3 127.0.0.1 >nul

pip install -r requirements.txt

ping -n 2 127.0.0.1 >nul

cls
color A
echo.
echo Setup completed successfully.

ping -n 3 127.0.0.1 >nul

echo.

start start.bat

exit