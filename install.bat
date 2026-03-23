@echo off
chcp 65001 >nul 2>&1
title Apple Music Wallpaper - Installer
color 0F

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   Apple Music Wallpaper - Install Wizard     ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: ── Step 1: Check Python ──
echo  [1/5] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [!] Python is not installed.
    echo      Download from: https://www.python.org/downloads/
    echo      IMPORTANT: Check "Add Python to PATH" during install.
    echo.
    echo  Press any key to open the download page...
    pause >nul
    start https://www.python.org/downloads/
    echo.
    echo  After installing Python, run this installer again.
    pause >nul
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo        Found Python %%v

:: ── Step 2: Install packages ──
echo.
echo  [2/5] Installing Python packages...
pip install fastapi uvicorn "winrt-Windows.Media.Control" "winrt-Windows.Foundation" "winrt-Windows.Foundation.Collections" "winrt-Windows.Storage.Streams" -q 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  [!] Package install failed. Try running as Administrator.
    pause >nul
    exit /b 1
)
echo        Done.

:: ── Step 3: Check Apple Music ──
echo.
echo  [3/5] Checking Apple Music...
powershell -NoProfile -Command "if (Get-AppxPackage *AppleMusic* 2>$null) { exit 0 } else { exit 1 }" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -Command "if (Get-AppxPackage *Apple.Music* 2>$null) { exit 0 } else { exit 1 }" >nul 2>&1
)
if %ERRORLEVEL% NEQ 0 (
    echo  [!] Apple Music not found.
    echo      Install from Microsoft Store:
    echo      https://apps.microsoft.com/detail/9PFHDD62MXS1
    echo.
    choice /C YN /M "  Open Microsoft Store? (Y/N)"
    if !ERRORLEVEL! EQU 1 start https://apps.microsoft.com/detail/9PFHDD62MXS1
    echo.
    echo  After installing Apple Music, you can continue.
    echo  Apple Music is required for this wallpaper to work.
    echo.
    pause
) else (
    echo        Found.
)

:: ── Step 4: Check Lively Wallpaper ──
echo.
echo  [4/5] Checking Lively Wallpaper...
powershell -NoProfile -Command "if (Get-AppxPackage *lively* 2>$null) { exit 0 } else { exit 1 }" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [!] Lively Wallpaper not found.
    echo      Install from Microsoft Store (FREE):
    echo      https://apps.microsoft.com/detail/9NTM2QC6QWS7
    echo.
    choice /C YN /M "  Open Microsoft Store? (Y/N)"
    if !ERRORLEVEL! EQU 1 start https://apps.microsoft.com/detail/9NTM2QC6QWS7
    echo.
    echo  After installing Lively Wallpaper, press any key to continue...
    pause >nul
) else (
    echo        Found.
)

:: ── Step 5: Create Desktop shortcut ──
echo.
echo  [5/5] Creating desktop shortcut...
set "SCRIPT_DIR=%~dp0"
set "SHORTCUT=%USERPROFILE%\Desktop\Apple Music Wallpaper.lnk"

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%SHORTCUT%'); $sc.TargetPath = '%SCRIPT_DIR%start.bat'; $sc.WorkingDirectory = '%SCRIPT_DIR%'; $sc.Description = 'Apple Music Wallpaper'; $sc.Save()"

if exist "%SHORTCUT%" (
    echo        Shortcut created on Desktop.
) else (
    echo        Could not create shortcut. You can run start.bat directly.
)

:: ── Done ──
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║          Installation Complete!              ║
echo  ╠══════════════════════════════════════════════╣
echo  ║                                              ║
echo  ║  How to use:                                 ║
echo  ║  1. Run "start.bat" or desktop shortcut      ║
echo  ║  2. In Lively Wallpaper, click [+]           ║
echo  ║  3. Select "Enter URL"                       ║
echo  ║  4. Type: http://127.0.0.1:8765              ║
echo  ║  5. Play music in Apple Music                ║
echo  ║                                              ║
echo  ║  (Lively remembers the URL after first use)  ║
echo  ╚══════════════════════════════════════════════╝
echo.

choice /C YN /M "  Launch now? (Y/N)"
if %ERRORLEVEL% EQU 1 (
    call "%SCRIPT_DIR%start.bat"
)
