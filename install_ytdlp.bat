@echo off
echo ================================
echo Installing yt-dlp for better YouTube support
echo ================================
echo.
echo yt-dlp is more reliable and actively maintained than pytube
echo It provides better compatibility with current YouTube
echo.
pause
echo.
echo Installing yt-dlp...
python -m pip install -U yt-dlp
echo.
if %errorlevel% equ 0 (
    echo ================================
    echo SUCCESS! yt-dlp installed successfully
    echo ================================
    echo.
    echo You can now run the YouTube downloader with enhanced support!
    echo Run: python main_gui.py
) else (
    echo ================================
    echo ERROR: Installation failed
    echo ================================
    echo Please try manually: pip install yt-dlp
)
echo.
pause
