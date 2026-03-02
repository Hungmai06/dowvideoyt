# 🎬 YouTube Channel Video Downloader

A powerful tool to download videos and thumbnails from YouTube channels with both Console and GUI interfaces!

## ✨ Features

- 📺 Download videos from entire YouTube channels
- 🖼️ Download high-quality thumbnails (automatically formatted to 16:9 aspect ratio)
- 🎥 Prefer 16:9 aspect ratio videos (standard widescreen format)
- 🔍 Filter videos by views, date, duration, or title
- 📊 Sort videos in multiple ways
- 🎬 Choose video quality (1080p, 720p, 480p, etc.)
- 📝 Multiple naming styles for files
- 🎨 Beautiful modern GUI interface
- ⚡ Multi-threaded downloads
- 📋 Detailed logging and progress tracking
- 🖼️ Thumbnails standardized to 640x360 (16:9 ratio)
- 🍪 **Optional cookies support** (disabled by default for best performance)

## 🚀 Quick Start

### ⚡ Recommended: Install yt-dlp first for best results
```bash
pip install yt-dlp
```
Or simply run: `install_ytdlp.bat`

### Method 1: GUI Version (Recommended)
```bash
python main_gui.py
```

### Method 2: Console Version
```bash
python main.py
```

## 📖 How to Use

### GUI Version

1. **Launch the Application**
   - Run `python main_gui.py`
   - A modern dark-themed window will open

2. **Enter Channel Information**
   - Paste the YouTube channel URL (e.g., `https://www.youtube.com/@channelname`)
   - Choose or browse to a download folder
   - Click "🔍 Get Channel Info"

3. **Configure Download Options**
   - **Videos to Fetch**: How many videos to load from the channel
   - **Min Views**: Filter videos with minimum view count
   - **Sort By**: Choose how to sort videos
   - **Quality**: Select video quality (Highest, 720p, 480p, etc.)
   - **Videos to Download**: How many videos to actually download
   - **Naming Style**: YouTube (with ID) or Simple (name only)
   - **Download Thumbnails**: Check to download thumbnails

4. **Start Download**
   - Click "⬇️ Start Download"
   - Watch the progress in the Activity Log
   - Wait for completion notification

### Console Version

1. **Run the Script**
   ```bash
   python main.py
   ```

2. **Follow the Prompts**
   - Enter YouTube channel URL
   - Enter download folder (or press Enter for 'downloads')
   - Choose number of videos to fetch
   - Configure filter options
   - Select quality and naming style
   - Confirm and start download

## 🎨 GUI Features

- **Modern Dark Theme**: Easy on the eyes with a beautiful color scheme
- **Real-time Logging**: See exactly what's happening
- **Color-coded Messages**: Success (green), errors (red), info (blue), warnings (yellow)
- **Progress Bar**: Visual feedback during operations
- **Easy Configuration**: All options in one clean interface

## 🛠️ Technical Details

### Requirements
- Python 3.7+
- **yt-dlp** (recommended - more reliable): `pip install yt-dlp`
- pytube (auto-installed as fallback)
- Pillow (auto-installed)
- tkinter (usually included with Python)

### Why yt-dlp?
- ✅ **More reliable** - actively maintained
- ✅ **Better compatibility** - works with current YouTube
- ✅ **Faster downloads** - optimized performance
- ✅ **More features** - better format selection

The app will use pytube as fallback if yt-dlp is not installed, but you may encounter errors like "channel_name: could not find match for patterns" with pytube.

### File Structure
```
downloads/
├── videos/          # Downloaded video files
└── thumbnails/      # Downloaded thumbnail images
```

### Naming Styles
- **YouTube Style**: `Video_Title_VideoID.mp4`
- **Simple Style**: `Video_Title.mp4`

### Quality Options
- **Highest**: Best available quality (prefers 16:9 aspect ratio)
- **Lowest**: Smallest file size
- **1080p, 720p, 480p, 360p, 240p**: Specific resolutions (prefers 16:9 aspect ratio)

### Aspect Ratio
- **Videos**: Automatically prioritizes 16:9 (widescreen) format when available
- **Thumbnails**: Automatically cropped/resized to 640x360 (16:9 ratio)
- **Display**: All media optimized for standard widescreen viewing

## 🐛 Bug Fixes

### Fixed in Latest Version:
- ✅ Path input now correctly handles quoted paths (e.g., `"E:\Video"`)
- ✅ Improved error handling for network issues
- ✅ Better file naming sanitization

## 💡 Tips

1. **For Large Channels**: Start with a smaller number of videos to test
2. **View Filtering**: Use min views to get only popular videos
3. **Quality vs Size**: Lower quality = smaller files, faster downloads
4. **Wait Time**: 5-second delay between downloads prevents rate limiting
5. **Existing Files**: The tool will ask before overwriting existing files

## 🔧 Troubleshooting

### ⚠️ IMPORTANT: Cookies are DISABLED by default for best performance!

### Common Issues:

**Problem**: ❌ **"Failed to parse JSON"** / **"JSON Decode Error"** (NEW!)
- **Why**: Cookies are causing YouTube to block ALL requests
- **Solution**: **DISABLE cookies checkbox in the app!**
  1. Open the app and find "☑ Enable Cookies" checkbox
  2. UNCHECK it (should be unchecked by default)
  3. App will use Android client (works better!)
  4. Only enable cookies for private/members-only videos
- **Detailed Guide**: See `FIX_JSON_DECODE_ERROR.md`

**Problem**: ❌ **HTTP Error 403: Forbidden**
- **Why**: YouTube blocks requests, missing Node.js
- **Solution** (in order):
  1. **Keep cookies DISABLED** (default, works best!)
  2. **Install Node.js**: https://nodejs.org/ (CRITICAL!)
  3. Only enable cookies if you need private/members videos
- **Quick Check**: Run `check_requirements.bat`
- **Detailed Guide**: See `fix_403_guide.md`

**Problem**: ❌ **"Requested format is not available"** / **"Only images are available"**
- **Why**: Cookies are enabled but expired/invalid
- **Solution**:
  1. **DISABLE cookies checkbox** (recommended - use Android client)
  2. Or export NEW cookies: Run `how_to_export_cookies.bat`
  3. Test cookies: Run `test_cookies.bat` to check validity
  4. Try different quality: "Highest" or "Lowest"
- **Detailed Guide**: See `FIX_FORMAT_NOT_AVAILABLE.md`

**Problem**: "No supported JavaScript runtime" warning
- **Solution**: Install Node.js (see above) - required for YouTube extraction

**Problem**: "channel_name: could not find match for patterns" error
- **Solution**: **Install yt-dlp** for better compatibility
  ```bash
  pip install yt-dlp
  ```
  Or run `install_ytdlp.bat`, then restart the application

**Problem**: "Invalid URL" error
- **Solution**: Make sure you're using the channel URL, not a video URL
- Format: `https://www.youtube.com/@channelname` or `https://www.youtube.com/c/channelname`

**Problem**: Download fails repeatedly
- **Solution**: Try a different quality setting or check your internet connection
- **Solution**: Make sure you have cookies.txt loaded

**Problem**: Quoted path error
- **Solution**: Don't use quotes around the path, or they will be automatically removed

**Problem**: Missing thumbnails
- **Solution**: Some videos may not have high-quality thumbnails available

## 📝 Notes

- Downloads are progressive (video+audio in one file)
- Thumbnails are automatically resized to 320x180 for consistency
- The tool respects YouTube's rate limits with automatic delays
- All special characters in filenames are automatically sanitized

## 🎯 Example Usage

### Download top 10 most viewed videos:
1. Set "Videos to Fetch": 50
2. Set "Min Views": 100000
3. Sort By: "Views (High to Low)"
4. Videos to Download: 10
5. Start Download

### Download recent videos only:
1. Set "Videos to Fetch": 30
2. Sort By: "Date (Newest)"
3. Videos to Download: 5
4. Start Download

## 🌟 Enjoy!

If you encounter any issues or have suggestions, please report them!
