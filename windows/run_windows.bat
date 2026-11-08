@echo off
title ScreenPen for Windows
echo Starting ScreenPen Overlay...
py -3 --version >nul 2>&1
if errorlevel 1 (
    python "%~dp0screenpen_windows.py"
) else (
    py -3 "%~dp0screenpen_windows.py"
)
if errorlevel 1 (
    echo.
    echo Python execution failed. Make sure Python 3 is installed.
    pause
    exit /b 1
)
