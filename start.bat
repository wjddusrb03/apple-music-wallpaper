@echo off
title Music Wallpaper

echo [1/4] Stopping old server...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8765') do taskkill /PID %%a /F >nul 2>&1

echo [2/4] Installing packages...
pip install fastapi uvicorn "winrt-Windows.Media.Control" "winrt-Windows.Foundation" "winrt-Windows.Foundation.Collections" "winrt-Windows.Storage.Streams" -q 2>nul

echo [3/4] Starting server...
start "MusicWallpaperServer" /MIN python server.py
timeout /t 2 /nobreak >nul

echo [4/4] Launching Lively Wallpaper...
tasklist /FI "IMAGENAME eq Lively.exe" 2>nul | find /i "Lively.exe" >nul
if %ERRORLEVEL%==0 (
    echo   Already running.
    goto :ready
)

REM Microsoft Store version
explorer.exe "shell:AppsFolder\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy!App" 2>nul
if %ERRORLEVEL%==0 (
    echo   Launched Lively Wallpaper.
    goto :ready
)

REM Fallback: search via PowerShell
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-AppxPackage *lively*).PackageFamilyName" 2^>nul`) do (
    if not "%%i"=="" (
        explorer.exe "shell:AppsFolder\%%i!App"
        echo   Launched Lively Wallpaper.
        goto :ready
    )
)

echo   Lively Wallpaper not found. Install from Microsoft Store.

:ready
echo.
echo ========================================
echo  Server: http://127.0.0.1:8765
echo ========================================
echo  First time? Add URL in Lively:
echo    [+] button - Enter URL
echo    http://127.0.0.1:8765
echo  After that, Lively remembers it.
echo ========================================
echo.
echo  Close this window to stop.
pause >nul

echo Shutting down...
taskkill /FI "WINDOWTITLE eq MusicWallpaperServer" /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8765') do taskkill /PID %%a /F >nul 2>&1
