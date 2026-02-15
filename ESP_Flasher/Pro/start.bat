@echo off
title ESP Flasher Pro - Made by LTX
color D
cls

ping -n 2 127.0.0.1 >nul

echo ========================
echo     Only for ESP !!!
echo ========================
echo.

ping -n 2 127.0.0.1 >nul

echo ==================================
echo        ESP Flasher Pro
echo           by LTX                
echo ==================================
echo.

ping -n 3 127.0.0.1 >nul

if not exist ESP_Flasher_Pro.py (
    echo [ERROR] ESP_Flasher_Pro.py not found.
    echo.
    pause
    exit
)

python ESP_Flasher_Pro.py

echo.
pause
exit