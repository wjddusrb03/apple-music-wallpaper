@echo off
cd /d "%~dp0"
title Apple Music Wallpaper

echo ==================================================
echo   Apple Music Wallpaper
echo ==================================================
echo.

REM Kill previous server only (by PID file)
if exist "server.pid" (
    set /p OLD_PID=<server.pid
    taskkill /F /PID %OLD_PID% >nul 2>&1
    del server.pid >nul 2>&1
)

if exist "python\python.exe" goto READY

echo [1/4] Downloading Python...
echo       First-time setup. Please wait...
echo.
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip' -OutFile 'python_embed.zip'"
if not exist "python_embed.zip" goto DOWNLOAD_FAIL

echo [2/4] Extracting Python...
mkdir python 2>nul
powershell -NoProfile -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python' -Force"
del python_embed.zip

echo [3/4] Installing pip...
powershell -NoProfile -Command "(Get-Content 'python\python312._pth') -replace '#import site','import site' | Set-Content 'python\python312._pth'"
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
python\python.exe get-pip.py --quiet
del get-pip.py

echo [4/4] Installing packages...
python\python.exe -m pip install --quiet fastapi uvicorn websockets winrt-Windows.Media.Control winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams
if errorlevel 1 goto INSTALL_FAIL

echo.
echo   Setup complete!
echo.

:READY
echo.
echo ==================================================
echo   Setup complete! Starting server...
echo ==================================================
echo.
echo   Lively Wallpaper setup (one time only):
echo     1. Click [+] button
echo     2. Select "Enter URL"
echo     3. Paste:  http://localhost:8765
echo     4. Done!
echo.
echo   Next time, use AppleMusicWallpaper.vbs
echo   to start without any CMD window.
echo.
echo ==================================================

start /min "AMW_Server" python\python.exe server.py
timeout /t 2 /nobreak >nul
start "" explorer.exe "shell:AppsFolder\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy!App"

echo.
echo   Server is running. Press any key to stop...
pause >nul
taskkill /F /FI "WINDOWTITLE eq AMW_Server" >nul 2>&1
echo Server stopped.
pause
goto :eof

:DOWNLOAD_FAIL
echo.
echo [ERROR] Download failed. Check your internet connection.
pause
goto :eof

:INSTALL_FAIL
echo.
echo [ERROR] Package install failed. Try running as Administrator.
pause
goto :eof
