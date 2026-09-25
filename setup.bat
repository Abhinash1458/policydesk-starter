@echo off
rem ============================================================
rem  PolicyDesk - one-click setup (Windows)
rem  TalentPath Academy - AI-Powered SDLC Workshop
rem
rem  Double-click this file. It checks what is missing, installs
rem  it, creates the virtual environment and the database, and
rem  tells you what to do next. Safe to run again at any time.
rem ============================================================
setlocal
title PolicyDesk - one-click setup
cd /d "%~dp0"

where powershell >nul 2>&1
if errorlevel 1 (
    echo.
    echo   PowerShell was not found on this machine.
    echo   Follow docs\setup-guide.md by hand, or ask the instructor.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
set "RC=%ERRORLEVEL%"

echo.
pause
exit /b %RC%
