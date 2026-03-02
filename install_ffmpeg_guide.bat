@echo off
echo ================================
echo FFmpeg Installation Guide
echo ================================
echo.
echo FFmpeg is required for downloading the best quality videos from YouTube.
echo Without it, you'll be limited to lower quality single-file formats.
echo.
echo INSTALLATION OPTIONS:
echo.
echo Option 1: Using Chocolatey (Recommended - Easiest)
echo   1. Open PowerShell as Administrator
echo   2. Install Chocolatey if you don't have it:
echo      Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
echo   3. Install FFmpeg:
echo      choco install ffmpeg
echo.
echo Option 2: Using Winget (Built into Windows 10/11)
echo   1. Open PowerShell or Command Prompt
echo   2. Run: winget install ffmpeg
echo.
echo Option 3: Manual Installation
echo   1. Download from: https://github.com/BtbN/FFmpeg-Builds/releases
echo   2. Extract the zip file
echo   3. Add the 'bin' folder to your system PATH
echo   4. Restart your computer
echo.
echo Option 4: Using Scoop
echo   1. Install Scoop: https://scoop.sh/
echo   2. Run: scoop install ffmpeg
echo.
echo ================================
echo After installation, restart the YouTube Downloader app
echo ================================
echo.
pause
