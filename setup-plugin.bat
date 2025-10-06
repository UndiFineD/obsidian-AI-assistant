@echo off
REM Obsidian AI Assistant - Simple Setup Launcher
REM This batch file provides an easy way to run the PowerShell setup script

echo ===============================================
echo    Obsidian AI Assistant - Quick Setup
echo ===============================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available on this system
    echo Please install PowerShell 5.1 or higher
    pause
    exit /b 1
)

REM Check if setup script exists
if not exist "setup-plugin.ps1" (
    echo ERROR: setup-plugin.ps1 not found
    echo Please make sure you're running this from the correct directory
    pause
    exit /b 1
)

echo Choose your setup option:
echo.
echo 1. Full Setup (Install plugin + Start backend server)
echo 2. Plugin Only (Just install plugin files)
echo 3. Backend Only (Just start the backend server)
echo 4. Advanced (Custom PowerShell parameters)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting full setup...
    powershell -ExecutionPolicy Bypass -File "setup-plugin.ps1"
) else if "%choice%"=="2" (
    echo Installing plugin files only...
    powershell -ExecutionPolicy Bypass -File "setup-plugin.ps1" -PluginOnly
) else if "%choice%"=="3" (
    echo Starting backend server only...
    powershell -ExecutionPolicy Bypass -File "setup-plugin.ps1" -BackendOnly
) else if "%choice%"=="4" (
    echo.
    echo Advanced options available:
    echo   -VaultPath "C:\path\to\vault"  : Specify vault location
    echo   -Force                         : Overwrite existing installation
    echo   -PluginOnly                   : Only install plugin files
    echo   -BackendOnly                  : Only start backend server
    echo.
    set /p params="Enter PowerShell parameters: "
    powershell -ExecutionPolicy Bypass -File "setup-plugin.ps1" %params%
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
if errorlevel 1 (
    echo Setup completed with errors. Check the output above.
) else (
    echo Setup completed successfully!
)
echo.
pause