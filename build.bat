@echo off
echo ================================================
echo   Apple Music Wallpaper - Build
echo ================================================
echo.

pip install pyinstaller pywebview pystray Pillow winrt-Windows.Media.Control winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams

echo.
echo [2/2] Building .exe ...
echo.

pyinstaller --onefile --noconsole --name "AppleMusicWallpaper" --add-data "wallpaper;wallpaper" app.py

echo.
echo ================================================
echo   Build complete!
echo   Output: dist\AppleMusicWallpaper.exe
echo ================================================
pause
