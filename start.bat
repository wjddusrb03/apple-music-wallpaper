@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Apple Music Wallpaper

echo ==================================================
echo   Apple Music Wallpaper
echo ==================================================
echo.

REM ── Kill old server if running ──
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8765.*LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)

REM ══════════════════════════════════════════
REM  First-time setup: Download embedded Python
REM ══════════════════════════════════════════
if not exist "python\python.exe" (
    echo [1/4] Downloading Python embeddable package...
    echo       This only happens once. Please wait...
    echo.

    powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip' -OutFile 'python_embed.zip' }" 2>nul

    if not exist "python_embed.zip" (
        echo [!] Download failed. Check your internet connection.
        pause
        exit /b 1
    )

    echo [2/4] Extracting Python...
    if not exist "python" mkdir python
    powershell -Command "& { Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python' -Force }" 2>nul
    del python_embed.zip 2>nul

    REM Enable site-packages
    powershell -Command "& { (Get-Content 'python\python312._pth') -replace '#import site','import site' | Set-Content 'python\python312._pth' }" 2>nul

    echo [3/4] Installing pip...
    powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' }" 2>nul
    python\python.exe get-pip.py --quiet 2>nul
    del get-pip.py 2>nul

    echo [4/4] Installing packages... (this may take a minute)
    python\python.exe -m pip install --quiet fastapi uvicorn winrt-Windows.Media.Control winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams 2>nul

    if %ERRORLEVEL% NEQ 0 (
        echo [!] Package install failed. Try running as Administrator.
        pause
        exit /b 1
    )

    echo.
    echo ==================================================
    echo   Setup complete!
    echo ==================================================
    echo.
)

REM ══════════════════════════════════════════
REM  Check Lively Wallpaper
REM ══════════════════════════════════════════
echo [*] Starting server...
echo.

REM Start server (minimized)
start /min "AMW Server" python\python.exe server.py

REM Wait for server to start
timeout /t 2 /nobreak >nul

REM Try to launch Lively Wallpaper
explorer.exe "shell:AppsFolder\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy!App" 2>nul

echo ==================================================
echo   Server running at http://localhost:8765
echo ==================================================
echo.
echo   If this is your first time:
echo   1. Open Lively Wallpaper
echo   2. Click [+] button
echo   3. Select "Enter URL"
echo   4. Paste: http://localhost:8765
echo   5. Done! (only need to do this once)
echo.
echo   Press any key to stop the server...
echo ==================================================
pause >nul

REM Stop server
taskkill /FI "WINDOWTITLE eq AMW Server" /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8765.*LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)
echo Server stopped.
