@echo off
title BIN_FLASHER .bin - Made by LTX
color D
cls

ping -n 2 127.0.0.1 >nul

echo ========================
echo     Only for ESP !!!
echo ========================
echo.

ping -n 2 127.0.0.1 >nul

echo ==================================
echo        ESP Flasher .bin      
echo           by LTX                
echo ==================================
echo.

ping -n 3 127.0.0.1 >nul

if not exist ESP_Flasher.py (
    echo [ERROR] ESP_Flasher.py not found.
    echo.
    pause
    exit
)

python ESP_Flasher.py

echo.
pause
exit