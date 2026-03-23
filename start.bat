@echo off
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
    echo [1/4] Downloading Python...
    echo       First-time setup. Please wait...
    echo.

    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip' -OutFile 'python_embed.zip'"

    if not exist "python_embed.zip" (
        echo [ERROR] Download failed. Check your internet connection.
        echo.
        pause
        exit /b 1
    )

    echo [2/4] Extracting Python...
    if not exist "python" mkdir python
    powershell -NoProfile -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python' -Force"
    del python_embed.zip 2>nul

    REM Enable site-packages
    powershell -NoProfile -Command "(Get-Content 'python\python312._pth') -replace '#import site','import site' | Set-Content 'python\python312._pth'"

    echo [3/4] Installing pip...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
    python\python.exe get-pip.py --quiet 2>nul
    del get-pip.py 2>nul

    echo [4/4] Installing packages...
    python\python.exe -m pip install --quiet fastapi uvicorn winrt-Windows.Media.Control winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams

    if errorlevel 1 (
        echo.
        echo [ERROR] Package install failed. Try running as Administrator.
        echo.
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
REM  Start server
REM ══════════════════════════════════════════
echo [*] Starting server...
echo.

start /min "AMW Server" python\python.exe server.py

timeout /t 2 /nobreak >nul

REM Try to launch Lively Wallpaper
start "" explorer.exe "shell:AppsFolder\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy!App" 2>nul

echo ==================================================
echo   Server running at http://localhost:8765
echo ==================================================
echo.
echo   First time? Do this once in Lively Wallpaper:
echo     1. Click [+] button
echo     2. Select "Enter URL"
echo     3. Paste:  http://localhost:8765
echo     4. Done!
echo.
echo   Press any key to stop the server...
echo ==================================================

pause >nul

taskkill /FI "WINDOWTITLE eq AMW Server" /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8765.*LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)
echo Server stopped.
pause
