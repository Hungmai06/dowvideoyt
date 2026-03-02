@echo off
echo ================================
echo Updating YouTube Download Libraries
echo ================================
echo.
echo This will update pytube and yt-dlp to the latest versions
echo to fix download errors and improve compatibility.
echo.
pause
echo.
echo Updating pytube...
python -m pip install --upgrade pytube
echo.
echo Updating yt-dlp...
python -m pip install --upgrade yt-dlp
echo.
echo Updating Pillow...
python -m pip install --upgrade Pillow
echo.
if %errorlevel% equ 0 (
    echo ================================
    echo SUCCESS! All libraries updated
    echo ================================
    echo.
    echo Please restart the YouTube Downloader application
    echo.
    echo If you still get errors:
    echo 1. The video might be private or members-only
    echo 2. The video might require age verification
    echo 3. The video might be region-locked
    echo 4. Try downloading a different video to test
) else (
    echo ================================
    echo ERROR: Update failed
    echo ================================
    echo Please check your internet connection
)
echo.
pause
