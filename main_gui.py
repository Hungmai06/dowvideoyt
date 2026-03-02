import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
from datetime import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import từ main.py
try:
    from pytube import YouTube, Channel
    from pytube.exceptions import VideoUnavailable, PytubeError
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
    from pytube import YouTube, Channel

try:
    from PIL import Image
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# Try to import yt-dlp for better YouTube support
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("▶️ YouTube Channel Video Downloader")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Color scheme - YouTube Theme (Red & White)
        self.colors = {
            'bg': '#FFFFFF',           # White background
            'fg': '#030303',           # Black text
            'primary': '#FF0000',      # YouTube Red
            'secondary': '#CC0000',    # Dark Red
            'success': '#065fd4',      # YouTube Blue
            'warning': '#ff9800',      # Orange
            'error': '#d32f2f',        # Error Red
            'input_bg': '#f9f9f9',     # Light gray input
            'button_bg': '#FF0000',    # YouTube Red button
            'button_hover': '#CC0000', # Dark red hover
            'accent': '#065fd4',       # Blue accent
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Variables
        self.downloader = None
        self.videos = []
        self.filtered_videos = []
        self.message_queue = queue.Queue()
        self.cookies_file = None
        self.use_cookies_var = tk.BooleanVar(value=False)  # Default: NO cookies (Android client better)
        self.stop_download = False  # Flag to stop download
        self.executor = None  # ThreadPoolExecutor reference
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.check_messages()
        
    def setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'], font=('Segoe UI', 9))
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'), foreground=self.colors['primary'])
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.colors['accent'])
        
        # Button style - YouTube Red
        style.configure('TButton',
                       background=self.colors['button_bg'],
                       foreground='#FFFFFF',
                       borderwidth=0,
                       relief='flat',
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', self.colors['button_hover'])],
                foreground=[('active', '#FFFFFF')])
        
        # Primary button style - YouTube Red
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='#FFFFFF',
                       font=('Segoe UI', 9, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary'])],
                 foreground=[('active', '#FFFFFF')])
        
        # Entry style
        style.configure('TEntry',
                       fieldbackground=self.colors['input_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='solid')
        
        # Combobox style
        style.configure('TCombobox',
                       fieldbackground=self.colors['input_bg'],
                       background=self.colors['button_bg'],
                       foreground=self.colors['fg'],
                       arrowcolor=self.colors['fg'],
                       borderwidth=1)
        
        # Progressbar style
        style.configure('TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['input_bg'],
                       borderwidth=0,
                       thickness=20)
        
    def create_widgets(self):
        """Create all GUI widgets with 2-column layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Left column
        main_frame.columnconfigure(1, weight=2)  # Right column (wider)
        main_frame.rowconfigure(0, weight=1)
        
        # === LEFT PANEL: CONTROLS ===
        left_panel = ttk.Frame(main_frame, padding="5")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(6, weight=1)  # Log section expands
        
        # Title with YouTube logo
        title_label = ttk.Label(left_panel, text="▶️ YouTube Downloader", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 8))
        
        # === INPUT SECTION ===
        input_frame = ttk.Frame(left_panel)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(1, weight=1)
        
        # Channel URL
        ttk.Label(input_frame, text="📌 URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=3)
        self.url_entry = ttk.Entry(input_frame, font=('Segoe UI', 9), foreground='gray')
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=3)
        self.url_entry.insert(0, "Enter YouTube channel URL (e.g., https://www.youtube.com/@channelname)")
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        self.url_placeholder = True
        
        # Download path
        ttk.Label(input_frame, text="📁 Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=3)
        path_frame = ttk.Frame(input_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=3)
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, font=('Segoe UI', 9), foreground='gray')
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 3))
        self.path_entry.insert(0, "Click Browse to select download folder...")
        self.path_entry.bind('<FocusIn>', self.on_path_focus_in)
        self.path_entry.bind('<FocusOut>', self.on_path_focus_out)
        self.path_placeholder = True
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder, width=8)
        browse_btn.grid(row=0, column=1)
        
        # === CHANNEL INFO SECTION ===
        info_frame = ttk.LabelFrame(left_panel, text=" Channel Info ", padding="5")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="📺 Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.channel_name_label = ttk.Label(info_frame, text="N/A", foreground=self.colors['primary'])
        self.channel_name_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text="🎬 Videos:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.video_count_label = ttk.Label(info_frame, text="N/A", foreground=self.colors['success'])
        self.video_count_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # === FILTER & OPTIONS SECTION ===
        options_frame = ttk.LabelFrame(left_panel, text=" Options ", padding="5")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)
        
        # Hidden defaults (not shown in UI)
        # Fetch: Empty = get ALL videos from channel
        self.max_videos_entry = ttk.Entry(options_frame, width=10)
        self.max_videos_entry.insert(0, "")  # Get all videos
        # Naming: Always YouTube style (with ID + sequence number)
        self.naming_combo = ttk.Combobox(options_frame, width=10, state='readonly')
        self.naming_combo['values'] = ('YouTube (with ID)', 'Simple (name only)')
        self.naming_combo.current(0)  # YouTube style
        # Thumbnails: Always download
        self.download_thumbnails_var = tk.BooleanVar(value=True)
        # Quality: Always Highest
        self.quality_combo = ttk.Combobox(options_frame, width=10, state='readonly')
        self.quality_combo['values'] = ('Highest', 'Lowest', '1080p', '720p', '480p', '360p', '240p')
        self.quality_combo.current(0)  # Highest
        
        # Min views filter
        ttk.Label(options_frame, text="📈 Min Views:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=3)
        self.min_views_entry = ttk.Entry(options_frame, width=10)
        self.min_views_entry.grid(row=0, column=1, sticky=tk.W, pady=3)
        self.min_views_entry.insert(0, "0")
        
        # Number of videos to download
        ttk.Label(options_frame, text="⬇️ Download:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=3)
        self.num_download_entry = ttk.Entry(options_frame, width=10)
        self.num_download_entry.grid(row=0, column=3, sticky=tk.W, pady=3)
        self.num_download_entry.insert(0, "5")
        # Bind event to update video list when number changes
        self.num_download_entry.bind('<KeyRelease>', lambda e: self.update_video_list_delayed())
        self.num_download_entry.bind('<FocusOut>', lambda e: self.update_video_list())
        
        # Sort by
        ttk.Label(options_frame, text="📊 Sort:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=3)
        self.sort_combo = ttk.Combobox(options_frame, width=15, state='readonly')
        self.sort_combo['values'] = ('Views (High to Low)', 'Views (Low to High)', 
                                     'Date (Newest)', 'Date (Oldest)', 
                                     'Duration (Longest)', 'Duration (Shortest)',
                                     'Title (A-Z)')
        self.sort_combo.current(0)
        self.sort_combo.grid(row=1, column=1, sticky=tk.W, pady=3)
        
        # Threads for parallel download
        ttk.Label(options_frame, text="⚡ Threads:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5), pady=3)
        self.threads_combo = ttk.Combobox(options_frame, width=8, state='readonly')
        self.threads_combo['values'] = ('1', '2', '3', '4', '5', '8', '10')
        self.threads_combo.current(2)  # Default: 3 threads
        self.threads_combo.grid(row=1, column=3, sticky=tk.W, pady=3)
        
        # === ACTION BUTTONS SECTION ===
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Get Info button
        self.get_info_btn = ttk.Button(buttons_frame, text="🔍 Get Info", 
                                       command=self.get_channel_info_thread, 
                                       style='Primary.TButton')
        self.get_info_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 3))
        
        # Start Download button
        self.download_btn = ttk.Button(buttons_frame, text="⬇️ Start Download", 
                                       command=self.start_download_thread, 
                                       style='Primary.TButton', state='disabled')
        self.download_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(3, 3))
        
        # Stop button
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Stop", 
                                   command=self.stop_download_process, 
                                   style='TButton', state='disabled')
        self.stop_btn.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(3, 0))
        
        # === PROGRESS SECTION ===
        progress_frame = ttk.Frame(left_panel)
        progress_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", foreground=self.colors['accent'])
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # === LOG SECTION ===
        log_frame = ttk.LabelFrame(left_panel, text=" Log ", padding="5")
        log_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                   height=12, 
                                                   wrap=tk.WORD,
                                                   bg=self.colors['input_bg'],
                                                   fg=self.colors['fg'],
                                                   font=('Consolas', 8),
                                                   relief='flat',
                                                   borderwidth=0)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('error', foreground=self.colors['error'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        self.log_text.tag_config('info', foreground=self.colors['primary'])
        self.log_text.tag_config('accent', foreground=self.colors['accent'])
        
        self.log("▶️ Welcome to YouTube Channel Video Downloader!", 'accent')
        self.log("Enter a YouTube channel URL to get started.", 'info')
        self.log("\n✅ Using Auto-Detect Mode (Best for 1080p quality)", 'success')
        self.log("   → Automatically selects best client for each video", 'info')
        self.log("   → No cookies needed - maximum compatibility!\n", 'success')
        
        # Check if yt-dlp is available
        if YT_DLP_AVAILABLE:
            self.log("✅ yt-dlp detected - using enhanced engine", 'success')
            # Check for FFmpeg
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.log("✅ FFmpeg detected - full quality downloads available", 'success')
                else:
                    self.log("⚠️ FFmpeg not found - may have limited quality options", 'warning')
                    self.log("💡 Install FFmpeg for best results: https://ffmpeg.org/download.html", 'info')
            except:
                self.log("⚠️ FFmpeg not found - may have limited quality options", 'warning')
                self.log("💡 Install FFmpeg for best results: https://ffmpeg.org/download.html", 'info')
            
            # Check for Node.js (important for avoiding 403 errors)
            try:
                import subprocess
                result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    node_version = result.stdout.strip()
                    self.log(f"✅ Node.js detected ({node_version}) - JavaScript support OK", 'success')
                else:
                    self.log("⚠️ Node.js not found - may cause 403 errors!", 'warning')
                    self.log("💡 Install Node.js: https://nodejs.org/ (IMPORTANT!)", 'warning')
                    self.log("💡 Or run: check_requirements.bat", 'info')
            except:
                self.log("⚠️ Node.js not found - HIGH RISK of 403 errors!", 'warning')
                self.log("💡 Install Node.js: https://nodejs.org/ (IMPORTANT!)", 'warning')
                self.log("💡 Or run: check_requirements.bat", 'info')
        else:
            self.log("⚠️ yt-dlp not found - using pytube (may have compatibility issues)", 'warning')
            self.log("💡 For better results, install yt-dlp: pip install yt-dlp", 'info')
        
        # === RIGHT PANEL: VIDEO LIST ===
        right_panel = ttk.Frame(main_frame, padding="5")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Title
        videos_title = ttk.Label(right_panel, text="📋 Video List", style='Title.TLabel')
        videos_title.grid(row=0, column=0, pady=(0, 5), sticky=tk.W)
        
        # Create Treeview for video list
        tree_frame = ttk.Frame(right_panel)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.video_tree = ttk.Treeview(tree_frame, 
                                       columns=('Title', 'Views', 'Duration', 'Progress'),
                                       show='tree headings',
                                       yscrollcommand=vsb.set,
                                       xscrollcommand=hsb.set,
                                       height=20)
        
        vsb.config(command=self.video_tree.yview)
        hsb.config(command=self.video_tree.xview)
        
        # Configure columns
        self.video_tree.column('#0', width=50, minwidth=50, anchor='center')  # STT
        self.video_tree.column('Title', width=300, minwidth=200, anchor='w')
        self.video_tree.column('Views', width=100, minwidth=80, anchor='e')
        self.video_tree.column('Duration', width=80, minwidth=60, anchor='center')
        self.video_tree.column('Progress', width=100, minwidth=80, anchor='center')
        
        # Configure headings
        self.video_tree.heading('#0', text='#', anchor='center')
        self.video_tree.heading('Title', text='📺 Title', anchor='w')
        self.video_tree.heading('Views', text='👁️ Views', anchor='e')
        self.video_tree.heading('Duration', text='⏱️ Duration', anchor='center')
        self.video_tree.heading('Progress', text='📊 Status', anchor='center')
        
        # Grid layout
        self.video_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure tag colors
        self.video_tree.tag_configure('downloading', background='#fff3cd')
        self.video_tree.tag_configure('completed', background='#d4edda')
        self.video_tree.tag_configure('failed', background='#f8d7da')
        self.video_tree.tag_configure('skipped', background='#e2e3e5')
        
        # Info label
        self.video_list_info = ttk.Label(right_panel, text="No videos loaded. Click 'Get Info' to fetch videos.", 
                                         foreground=self.colors['warning'])
        self.video_list_info.grid(row=2, column=0, pady=(5, 0), sticky=tk.W)
        
    def on_url_focus_in(self, event):
        """Clear placeholder text when URL entry is focused"""
        if self.url_placeholder:
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(foreground=self.colors['fg'])
            self.url_placeholder = False
    
    def on_url_focus_out(self, event):
        """Restore placeholder if entry is empty"""
        if not self.url_entry.get().strip():
            self.url_entry.insert(0, "Enter YouTube channel URL (e.g., https://www.youtube.com/@channelname)")
            self.url_entry.config(foreground='gray')
            self.url_placeholder = True
    
    def on_path_focus_in(self, event):
        """Clear placeholder text when path entry is focused"""
        if self.path_placeholder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.config(foreground=self.colors['fg'])
            self.path_placeholder = False
    
    def on_path_focus_out(self, event):
        """Restore placeholder if entry is empty"""
        if not self.path_entry.get().strip():
            self.path_entry.insert(0, "Click Browse to select download folder...")
            self.path_entry.config(foreground='gray')
            self.path_placeholder = True
    
    def on_cookies_focus_in(self, event):
        """Cookies feature removed - no-op function for compatibility"""
        pass
    
    def on_cookies_focus_out(self, event):
        """Cookies feature removed - no-op function for compatibility"""
        pass
    
    def browse_cookies(self):
        """Cookies feature removed - no-op function for compatibility"""
        pass
    
    def on_cookies_toggle(self):
        """Cookies feature removed - using auto-detect mode (best compatibility)"""
        pass
    
    def clean_channel_url(self, url):
        """Clean and validate channel URL"""
        url = url.strip()
        
        # Remove placeholder text remnants
        if 'Enter YouTube' in url or 'e.g.' in url:
            return ''
        
        # Handle common issues
        # Remove duplicate https://www.youtube.com/
        if url.count('https://www.youtube.com/') > 1:
            # Extract the last part after the duplicate
            parts = url.split('https://www.youtube.com/')
            url = 'https://www.youtube.com/' + parts[-1]
        
        # Remove trailing @ if present
        url = url.rstrip('@')
        
        # Ensure it starts with http
        if not url.startswith('http'):
            if url.startswith('www.youtube.com'):
                url = 'https://' + url
            elif url.startswith('youtube.com'):
                url = 'https://www.' + url
            elif url.startswith('@'):
                url = 'https://www.youtube.com/' + url
        
        # Validate it's a YouTube URL
        if 'youtube.com' not in url:
            return ''
        
        return url
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
    
    def log(self, message, tag='normal'):
        """Add message to log with timestamp and color"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'info')
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
    
    def check_messages(self):
        """Check message queue and update log"""
        try:
            while True:
                msg, tag = self.message_queue.get_nowait()
                self.log(msg, tag)
        except queue.Empty:
            pass
        self.root.after(100, self.check_messages)
    
    def queue_log(self, message, tag='normal'):
        """Add log message from thread"""
        self.message_queue.put((message, tag))
    
    def get_channel_info_thread(self):
        """Get channel info in separate thread"""
        thread = threading.Thread(target=self.get_channel_info, daemon=True)
        thread.start()
    
    def get_channel_info(self):
        """Get channel information"""
        try:
            # Disable button and show progress
            self.get_info_btn.config(state='disabled')
            self.download_btn.config(state='disabled')
            self.progress_bar.start()
            self.progress_label.config(text="Fetching channel information...")
            
            # Clean and validate URL
            channel_url = self.clean_channel_url(self.url_entry.get())
            download_path = self.path_entry.get().strip().strip('"').strip("'")
            
            # Get cookies file if provided AND enabled
            self.cookies_file = None
            if self.use_cookies_var.get():  # Only use cookies if checkbox is enabled
                cookies_text = self.cookies_entry.get().strip()
                if cookies_text and not self.cookies_placeholder and 'Optional' not in cookies_text:
                    cookies_path = cookies_text.strip('"').strip("'")
                    if os.path.exists(cookies_path):
                        self.cookies_file = cookies_path
                        self.queue_log(f"🍪 Cookies ENABLED: {os.path.basename(self.cookies_file)}", 'info')
                        self.queue_log(f"⚠️ Using Web client (if errors, disable cookies!)", 'warning')
                    else:
                        self.queue_log(f"⚠️ Cookies file not found: {cookies_path}", 'warning')
                else:
                    self.queue_log(f"⚠️ Cookies enabled but no file selected!", 'warning')
            else:
                self.queue_log(f"📱 Cookies DISABLED - Using Android client (recommended)", 'success')
            
            if not channel_url:
                self.queue_log("❌ Please enter a valid YouTube channel URL!", 'error')
                self.queue_log("   Example: https://www.youtube.com/@channelname", 'warning')
                return
            
            if not download_path:
                self.queue_log("❌ Please select a download folder first!", 'error')
                self.queue_log("   Click Browse button to choose folder", 'warning')
                return
            
            self.queue_log(f"🔍 Fetching info from: {channel_url}", 'info')
            
            # Try yt-dlp first if available
            if YT_DLP_AVAILABLE:
                self.queue_log("📡 Using yt-dlp (more reliable)...", 'info')
                channel_info = self.get_channel_info_ytdlp(channel_url, download_path)
                if channel_info and channel_info.get('status') != 'error':
                    return
            
            # yt-dlp is required
            self.queue_log("❌ yt-dlp is required for this application!", 'error')
            self.queue_log("\n💡 Please install yt-dlp:", 'warning')
            self.queue_log("   pip install yt-dlp", 'info')
            self.queue_log("   Then restart the application.", 'info')
            return
            
        except Exception as e:
            self.queue_log(f"❌ Error: {str(e)}", 'error')
        finally:
            self.progress_bar.stop()
            self.progress_label.config(text="Ready")
            self.get_info_btn.config(state='normal')
    
    def filter_videos(self):
        """Filter and sort videos"""
        try:
            if not self.videos:
                return
            
            # Get filter parameters
            min_views = int(self.min_views_entry.get() or 0)
            
            # Get sort parameters
            sort_choice = self.sort_combo.current()
            sort_map = {
                0: ('views', True),   # High to Low
                1: ('views', False),  # Low to High
                2: ('date', True),    # Newest
                3: ('date', False),   # Oldest
                4: ('duration', True),   # Longest
                5: ('duration', False),  # Shortest
                6: ('title', False)   # A-Z
            }
            sort_by, reverse = sort_map.get(sort_choice, ('views', True))
            
            self.queue_log(f"🔧 Filtering videos (min views: {min_views:,})...", 'info')
            
            # Manual filtering if using yt-dlp
            if YT_DLP_AVAILABLE and not hasattr(self.downloader, 'filter_videos'):
                # Filter with None handling
                filtered = [v for v in self.videos if (v.get('views') or 0) >= min_views]
                
                # Sort with None handling
                sort_keys = {
                    'views': lambda x: x.get('views') or 0,
                    'date': lambda x: x.get('publish_date') or 0,
                    'title': lambda x: x.get('title', ''),
                    'duration': lambda x: x.get('length') or 0
                }
                if sort_by in sort_keys:
                    filtered.sort(key=sort_keys[sort_by], reverse=reverse)
                
                self.filtered_videos = filtered
                self.downloader.filtered_videos = filtered
            else:
                # Use downloader's filter method
                self.filtered_videos = self.downloader.filter_videos(
                    min_views=min_views,
                    sort_by=sort_by,
                    reverse=reverse
                )
            
            # Show clear message about filtering results
            if len(self.filtered_videos) < len(self.videos):
                filtered_out = len(self.videos) - len(self.filtered_videos)
                self.queue_log(f"✅ Filter complete: {len(self.filtered_videos)} videos ≥ {min_views:,} views (excluded {filtered_out})", 'success')
            else:
                self.queue_log(f"✅ All {len(self.filtered_videos)} videos match min views: {min_views:,}", 'success')
            
            # Show top 5 videos
            self.queue_log("📋 Top videos:", 'accent')
            for i, video in enumerate(self.filtered_videos[:5], 1):
                views = video.get('views') or 0
                length = video.get('length') or 0
                views_str = f"{views:,}".replace(',', '.')
                duration = time.strftime('%H:%M:%S', time.gmtime(length))
                self.queue_log(f"   {i}. {video.get('title', 'Unknown')[:60]}", 'normal')
                self.queue_log(f"      👁️ {views_str} views | ⏱️ {duration}", 'normal')
            
            if len(self.filtered_videos) > 5:
                self.queue_log(f"   ... and {len(self.filtered_videos) - 5} more", 'normal')
            
            # Update video list in right panel
            self.update_video_list()
                
        except Exception as e:
            self.queue_log(f"❌ Filter error: {str(e)}", 'error')
    
    def update_video_list(self):
        """Update video list in right panel - only show videos that will be downloaded"""
        try:
            # Clear existing items
            for item in self.video_tree.get_children():
                self.video_tree.delete(item)
            
            if not self.filtered_videos:
                self.video_list_info.config(text="No videos after filtering.", foreground=self.colors['warning'])
                return
            
            # Get number of videos to download
            requested_count = int(self.num_download_entry.get() or len(self.filtered_videos))
            num_to_show = min(requested_count, len(self.filtered_videos))
            
            # Populate video list - ONLY show videos that will be downloaded
            for i, video in enumerate(self.filtered_videos[:num_to_show], 1):
                title = video.get('title', 'Unknown')[:50]
                views = video.get('views') or 0
                views_str = f"{views:,}".replace(',', '.')
                length = video.get('length') or 0
                duration = time.strftime('%H:%M:%S', time.gmtime(length)) if length > 0 else 'N/A'
                
                # Insert into tree
                item_id = self.video_tree.insert('', 'end', text=str(i),
                                                 values=(title, views_str, duration, 'Ready'))
                
                # Store video info with item_id for later reference
                video['tree_item_id'] = item_id
            
            # Update info label
            if num_to_show < len(self.filtered_videos):
                self.video_list_info.config(
                    text=f"📊 Showing {num_to_show} videos (of {len(self.filtered_videos)} available) - ready to download",
                    foreground=self.colors['success']
                )
            else:
                self.video_list_info.config(
                    text=f"📊 Total: {num_to_show} videos ready for download",
                    foreground=self.colors['success']
                )
            
        except Exception as e:
            self.queue_log(f"❌ Error updating video list: {str(e)}", 'error')
    
    def update_video_list_delayed(self):
        """Update video list with delay to avoid too many updates while typing"""
        # Cancel previous scheduled update if exists
        if hasattr(self, '_update_timer') and self._update_timer:
            self.root.after_cancel(self._update_timer)
        # Schedule new update after 500ms
        self._update_timer = self.root.after(500, self.update_video_list)
    
    def update_video_progress(self, video_info, status, progress=''):
        """Update video progress in tree"""
        try:
            item_id = video_info.get('tree_item_id')
            if not item_id:
                return
            
            # Get current values
            values = list(self.video_tree.item(item_id, 'values'))
            
            # Update status column
            if status == 'downloading':
                values[3] = progress if progress else '⬇️ Downloading...'
                self.video_tree.item(item_id, values=values, tags=('downloading',))
            elif status == 'success':
                values[3] = '✅ Complete'
                self.video_tree.item(item_id, values=values, tags=('completed',))
            elif status == 'skipped':
                values[3] = '⏭️ Skipped'
                self.video_tree.item(item_id, values=values, tags=('skipped',))
            elif status == 'error':
                values[3] = '❌ Failed'
                self.video_tree.item(item_id, values=values, tags=('failed',))
            
            # Scroll to current item
            self.video_tree.see(item_id)
            
        except Exception as e:
            pass  # Silently fail - don't interrupt download
    
    def start_download_thread(self):
        """Start download in separate thread"""
        self.stop_download = False  # Reset stop flag
        thread = threading.Thread(target=self.download_videos, daemon=True)
        thread.start()
    
    def stop_download_process(self):
        """Stop the download process"""
        if not self.stop_download:
            self.stop_download = True
            self.queue_log("\n⛔ STOP REQUESTED - Cancelling downloads...", 'warning')
            self.queue_log("   Current downloads will finish, new ones will be cancelled.", 'info')
            self.stop_btn.config(state='disabled')
    
    def _download_single_video(self, i, video_info, quality, naming_style, download_thumbnails, num_to_download):
        """Download a single video (called by ThreadPoolExecutor)"""
        try:
            self.queue_log(f"\n[{i}/{num_to_download}] {video_info['title'][:60]}", 'accent')
            
            # Update tree: Start downloading
            self.root.after(0, lambda: self.update_video_progress(video_info, 'downloading', '⏳ Starting...'))
            
            # Create filenames with sequence number
            include_id = (naming_style == 'youtube')
            base_filename = self.generate_filename(video_info, include_id, sequence_number=i)
            video_filename = f"{base_filename}.mp4"
            video_full_path = os.path.join(self.downloader.video_path, video_filename)
            
            # Check if exists
            if os.path.exists(video_full_path):
                file_size = os.path.getsize(video_full_path) / (1024 * 1024)
                self.queue_log(f"   ⏭️ File already exists ({file_size:.1f} MB), skipping...", 'warning')
                self.root.after(0, lambda: self.update_video_progress(video_info, 'skipped'))
                return {'status': 'skipped', 'title': video_info['title'], 'filesize_mb': file_size}
            
            # Download thumbnail first
            if download_thumbnails:
                self.root.after(0, lambda: self.update_video_progress(video_info, 'downloading', '🖼️ Thumbnail...'))
                self.queue_log(f"   🖼️ Downloading thumbnail...", 'info')
                thumbnail_path = self.download_thumbnail_manual(video_info, sequence_number=i)
                if thumbnail_path:
                    self.queue_log(f"   ✅ Thumbnail saved", 'success')
            
            # Download video with yt-dlp
            self.root.after(0, lambda: self.update_video_progress(video_info, 'downloading', '⬇️ Downloading...'))
            self.queue_log(f"   🎬 Downloading video...", 'info')
            
            if not YT_DLP_AVAILABLE:
                self.queue_log(f"   ❌ yt-dlp not available", 'error')
                self.root.after(0, lambda: self.update_video_progress(video_info, 'error'))
                return {'status': 'error', 'message': 'yt-dlp not available'}
            
            # Format selection - Ensure audio is always included
            # Priority: 1080p with audio > 720p with audio > best available with audio > best overall
            if quality == 'highest':
                format_str = 'bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1080]+bestaudio/bestvideo[height>=720]+bestaudio/bestvideo*+bestaudio/best'
            elif quality == 'lowest':
                format_str = 'worstvideo+worstaudio/worst'
            else:
                height = quality.replace('p', '')
                format_str = f'bestvideo[height>={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>={height}]+bestaudio/bestvideo*+bestaudio/best'
            
            # yt-dlp options - AUTO DETECT mode with proper audio/video merge
            # Force mp4 output format and ensure ffmpeg is used for merging
            base_path = video_full_path.rsplit('.', 1)[0]  # Remove .mp4 extension
            ydl_opts = {
                'format': format_str,
                'outtmpl': base_path,  # Without extension
                'merge_output_format': 'mp4',  # Force merge to mp4
                'postprocessors': [{  # Ensure audio is embedded
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'keepvideo': False,  # Remove separate streams after merge
                'quiet': False,
                'no_warnings': False,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_color': True,
                'extractor_retries': 5,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'retries': 10,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
            }
            
            # Download with yt-dlp
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_info['url'], download=True)
                
                # Get file size
                file_size = 0
                if os.path.exists(video_full_path):
                    file_size = os.path.getsize(video_full_path) / (1024 * 1024)  # Convert to MB
                    self.queue_log(f"   ✅ Downloaded: {file_size:.1f} MB", 'success')
                    self.root.after(0, lambda: self.update_video_progress(video_info, 'success'))
                    return {
                        'status': 'success',
                        'title': video_info['title'],
                        'filesize_mb': file_size,
                        'video_path': video_full_path
                    }
                else:
                    # File not found - list files in directory for debugging
                    import glob
                    video_dir = os.path.dirname(video_full_path)
                    expected_basename = os.path.basename(base_path)
                    similar_files = glob.glob(os.path.join(video_dir, f"{expected_basename}*"))
                    
                    error_msg = f'Expected file not found: {os.path.basename(video_full_path)}'
                    if similar_files:
                        self.queue_log(f"   ⚠️ Similar files found: {[os.path.basename(f) for f in similar_files]}", 'warning')
                        # Check if any similar file exists with different extension
                        for similar_file in similar_files:
                            if os.path.exists(similar_file) and similar_file.endswith('.mp4'):
                                file_size = os.path.getsize(similar_file) / (1024 * 1024)
                                self.queue_log(f"   ✅ Found alternative: {file_size:.1f} MB", 'success')
                                self.root.after(0, lambda: self.update_video_progress(video_info, 'success'))
                                return {
                                    'status': 'success',
                                    'title': video_info['title'],
                                    'filesize_mb': file_size,
                                    'video_path': similar_file
                                }
                    
                    self.queue_log(f"   ❌ {error_msg}", 'error')
                    self.root.after(0, lambda: self.update_video_progress(video_info, 'error'))
                    return {'status': 'error', 'message': error_msg}
                    
        except Exception as e:
            self.queue_log(f"   ❌ Error: {str(e)[:100]}", 'error')
            self.root.after(0, lambda: self.update_video_progress(video_info, 'error'))
            return {'status': 'error', 'message': str(e)}
    
    def download_videos(self):
        """Download videos with multi-threading support"""
        try:
            # Disable/Enable buttons
            self.download_btn.config(state='disabled')
            self.get_info_btn.config(state='disabled')
            self.stop_btn.config(state='normal')  # Enable stop button
            self.progress_bar.start()
            
            if not self.filtered_videos:
                self.queue_log("❌ No videos to download! Please get channel info first.", 'error')
                return
            
            # Get parameters - check available videos after min_views filter
            min_views_filter = int(self.min_views_entry.get() or 0)
            requested_count = int(self.num_download_entry.get() or len(self.filtered_videos))
            available_count = len(self.filtered_videos)  # After min_views filter
            num_to_download = min(requested_count, available_count)
            
            # Show clear message about min_views filter impact
            if available_count < requested_count:
                self.queue_log(f"⚠️ FILTER IMPACT:", 'warning')
                self.queue_log(f"   • You requested: {requested_count} videos", 'info')
                self.queue_log(f"   • Min views filter: ≥ {min_views_filter:,} views", 'info')
                self.queue_log(f"   • Videos available: {available_count} (after filter)", 'warning')
                self.queue_log(f"   → Will download: {num_to_download} videos only", 'success')
            else:
                self.queue_log(f"✅ Sufficient videos: {available_count} available ≥ {requested_count} requested", 'success')
            
            # Get number of threads
            max_workers = int(self.threads_combo.get())
            
            quality_map = {
                0: 'highest', 1: 'lowest', 2: '1080p', 
                3: '720p', 4: '480p', 5: '360p', 6: '240p'
            }
            quality = quality_map.get(self.quality_combo.current(), 'highest')
            
            naming_style = 'youtube' if self.naming_combo.current() == 0 else 'simple'
            download_thumbnails = self.download_thumbnails_var.get()
            
            self.queue_log("="*60, 'accent')
            self.queue_log(f"⬇️ STARTING DOWNLOAD", 'accent')
            self.queue_log(f"   Min views: ≥ {min_views_filter:,} → {available_count} videos available", 'info')
            self.queue_log(f"   Downloading: {num_to_download} videos", 'success')
            self.queue_log(f"   Quality: {quality} | Naming: {naming_style}", 'info')
            self.queue_log(f"   Thumbnails: {'Yes' if download_thumbnails else 'No'}", 'info')
            self.queue_log(f"   🎯 Mode: Auto-detect with audio guarantee (FFmpeg merge)", 'success')
            self.queue_log(f"   ⚡ Threads: {max_workers} (Parallel downloads)", 'info')
            self.queue_log("="*60, 'accent')
            
            # Prepare download tasks
            download_tasks = []
            for i, video_info in enumerate(self.filtered_videos[:num_to_download], 1):
                download_tasks.append((i, video_info, quality, naming_style, download_thumbnails, num_to_download))
            
            # Download with ThreadPoolExecutor
            downloaded = []
            skipped = []
            failed = []
            completed_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                self.executor = executor  # Store reference for cancellation
                
                # Submit all tasks
                future_to_video = {}
                for task in download_tasks:
                    # Check if stop was requested before submitting
                    if self.stop_download:
                        self.queue_log("⛔ Stop requested - not submitting remaining tasks", 'warning')
                        break
                    future = executor.submit(self._download_single_video, *task)
                    future_to_video[future] = task
                
                # Process completed downloads
                for future in as_completed(future_to_video):
                    # Check if stop was requested
                    if self.stop_download:
                        self.queue_log("⛔ Stop requested - cancelling remaining downloads...", 'warning')
                        # Cancel remaining futures
                        for f in future_to_video:
                            if not f.done():
                                f.cancel()
                        break
                    
                    completed_count += 1
                    task = future_to_video[future]
                    video_num = task[0]
                    video_title = task[1].get('title', 'Unknown')[:50]
                    
                    try:
                        result = future.result()
                        if result:
                            status = result.get('status')
                            if status == 'success':
                                downloaded.append(result)
                                self.queue_log(f"   ✅ [{video_num}] Success: {video_title}", 'success')
                            elif status == 'skipped':
                                skipped.append(result)
                                self.queue_log(f"   ⏭️ [{video_num}] Skipped: {video_title} (already exists)", 'warning')
                            else:  # error
                                failed.append(result)
                                error_msg = result.get('message', 'Unknown error')[:50]
                                self.queue_log(f"   ❌ [{video_num}] Failed: {video_title} - {error_msg}", 'error')
                        else:
                            failed.append({'status': 'error', 'message': 'No result returned'})
                            self.queue_log(f"   ❌ [{video_num}] Failed: No result", 'error')
                        
                        # Update progress
                        self.root.after(0, lambda c=completed_count, t=num_to_download: 
                                      self.progress_label.config(text=f"Processed {c}/{t} videos..."))
                    except Exception as e:
                        failed.append({'status': 'error', 'message': str(e)})
                        self.queue_log(f"   ❌ [{video_num}] Thread error: {str(e)[:100]}", 'error')
            # Summary
            self.queue_log("\n" + "="*60, 'accent')
            
            if self.stop_download:
                self.queue_log(f"⏹️ DOWNLOAD STOPPED BY USER", 'warning')
                self.queue_log(f"   Completed before stop: {completed_count}/{num_to_download} videos", 'info')
            
            total_success = len(downloaded) + len(skipped)
            
            if total_success == 0:
                self.queue_log(f"❌ DOWNLOAD FAILED - No videos available", 'error')
                self.queue_log(f"   Attempted: {num_to_download} videos", 'warning')
                self.queue_log(f"   Failed: {len(failed)} videos", 'error')
                
                # Show error details
                self.queue_log(f"\n   💡 Possible reasons:", 'warning')
                self.queue_log(f"   - Videos may be private/deleted/restricted", 'info')
                self.queue_log(f"   - Internet connection issues", 'info')
                self.queue_log(f"   - YouTube blocking requests", 'info')
                self.queue_log(f"   - Check video URLs are valid", 'info')
            else:
                self.queue_log(f"✅ PROCESS COMPLETE!", 'success')
                self.queue_log(f"   Newly downloaded: {len(downloaded)} video(s)", 'success')
                if len(skipped) > 0:
                    self.queue_log(f"   Already existed: {len(skipped)} video(s)", 'info')
                if len(failed) > 0:
                    self.queue_log(f"   Failed: {len(failed)} video(s)", 'warning')
                self.queue_log(f"   Total available: {total_success}/{num_to_download} video(s)", 'success')
            
            # Calculate total size (only newly downloaded files)
            total_size = sum(v.get('filesize_mb', 0) for v in downloaded)
            if total_size > 0:
                self.queue_log(f"   New download size: {total_size:.1f} MB", 'info')
            
            # Show completion dialog if any videos available
            if total_success > 0:
                success_msg = f"Process completed successfully!\n\n"
                success_msg += f"✅ Newly downloaded: {len(downloaded)} video(s)"
                if total_size > 0:
                    success_msg += f" ({total_size:.1f} MB)"
                success_msg += "\n"
                
                if len(skipped) > 0:
                    success_msg += f"⏭️ Already existed: {len(skipped)} video(s)\n"
                
                if len(failed) > 0:
                    success_msg += f"❌ Failed: {len(failed)} video(s)\n"
                
                success_msg += f"\n📊 Total available: {total_success}/{num_to_download}\n"
                success_msg += f"📁 Location: {self.downloader.download_path}"
                
                self.root.after(0, lambda msg=success_msg: messagebox.showinfo(
                    "✅ Process Complete",
                    msg
                ))
            else:
                # All failed
                error_msg = f"Failed to download {num_to_download} video(s)!\n\n"
                error_msg += "Possible reasons:\n"
                error_msg += "• Videos are private/deleted\n"
                error_msg += "• Internet connection issue\n" 
                error_msg += "• YouTube blocking requests\n\n"
                error_msg += "Check the log for details."
                
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "❌ Download Failed",
                    msg
                ))
            self.queue_log(f"   Location: {self.downloader.download_path}", 'info')
            self.queue_log("="*60, 'accent')
            
        except Exception as e:
            self.queue_log(f"❌ Download error: {str(e)}", 'error')
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
        finally:
            self.progress_bar.stop()
            self.progress_label.config(text="Ready")
            self.download_btn.config(state='normal')
            self.get_info_btn.config(state='normal')
            self.stop_btn.config(state='disabled')  # Disable stop button
            self.executor = None  # Clear executor reference
    
    def get_channel_info_ytdlp(self, channel_url, download_path):
        """Get channel info using yt-dlp (more reliable)"""
        try:
            # First, try to get channel videos specifically
            # YouTube channel videos URL format
            videos_url = channel_url.rstrip('/') + '/videos'
            
            self.queue_log(f"🔍 Scanning ALL videos on channel (excluding shorts)...", 'info')
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get info
                # No playlistend - get ALL videos
            }
            
            # Add cookies if available
            if self.cookies_file and os.path.exists(self.cookies_file):
                ydl_opts['cookiefile'] = self.cookies_file
                self.queue_log(f"🍪 Using cookies for authentication", 'info')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videos_url, download=False)
                
                if not info:
                    return {'status': 'error', 'message': 'Could not fetch channel info'}
                
                channel_name = info.get('channel', info.get('uploader', info.get('title', 'Unknown Channel')))
                entries = info.get('entries', [])
                
                # Filter out non-video entries (playlists, etc.)
                video_entries = []
                for entry in entries:
                    if not entry:
                        continue
                    # Check if this is actually a video (not a playlist)
                    entry_type = entry.get('_type', 'video')
                    if entry_type == 'url' or entry_type == 'video':
                        video_entries.append(entry)
                    elif entry_type == 'playlist':
                        # This is a playlist, skip it or we could expand it
                        self.queue_log(f"⚠️ Skipping playlist: {entry.get('title', 'Unknown')}", 'warning')
                        continue
                
                video_count = len(video_entries)
                
                if video_count == 0:
                    # Try alternative: get channel main page
                    self.queue_log("⚠️ No videos found in /videos tab, trying main channel page...", 'warning')
                    info = ydl.extract_info(channel_url, download=False)
                    entries = info.get('entries', [])
                    video_entries = [e for e in entries if e and e.get('_type', 'video') in ['url', 'video']]
                    video_count = len(video_entries)
                    channel_name = info.get('channel', info.get('uploader', info.get('title', 'Unknown Channel')))
                
                # Update GUI
                self.root.after(0, lambda: self.channel_name_label.config(text=channel_name))
                self.root.after(0, lambda: self.video_count_label.config(text=str(video_count)))
                
                self.queue_log(f"✅ Channel: {channel_name}", 'success')
                self.queue_log(f"📊 Found {video_count} videos", 'success')
                
                if video_count == 0:
                    self.queue_log("⚠️ No videos found! Channel might be empty or private.", 'warning')
                    return {'status': 'error', 'message': 'No videos found in channel'}
                
                # Convert to our format and filter out shorts/reels
                self.videos = []
                shorts_count = 0
                for entry in video_entries:
                    if not entry:
                        continue
                    
                    video_id = entry.get('id', '')
                    if not video_id:
                        # Try to extract from url
                        url = entry.get('url', '')
                        if 'watch?v=' in url:
                            video_id = url.split('watch?v=')[1].split('&')[0]
                        else:
                            continue
                    
                    # Get duration - filter out shorts (< 60 seconds)
                    duration = entry.get('duration') or 0
                    if duration > 0 and duration < 60:
                        shorts_count += 1
                        continue  # Skip shorts/reels
                    
                    video_data = {
                        'title': entry.get('title', 'Unknown'),
                        'url': entry.get('url') if entry.get('url', '').startswith('http') else f"https://www.youtube.com/watch?v={video_id}",
                        'video_id': video_id,
                        'views': entry.get('view_count') or 0,  # Ensure not None
                        'length': duration,
                        'publish_date': None,  # yt-dlp doesn't always provide this in flat extraction
                        'description': entry.get('description', '')[:100] if entry.get('description') else '',
                        'filename': self.sanitize_filename(entry.get('title', 'video'))
                    }
                    self.videos.append(video_data)
                
                self.queue_log(f"✅ Scanned {video_count} total entries", 'success')
                self.queue_log(f"📹 Regular videos: {len(self.videos)} | 🎬 Shorts excluded: {shorts_count}", 'info')
                
                # Update video count with actual videos (excluding shorts)
                self.root.after(0, lambda: self.video_count_label.config(text=str(len(self.videos))))
                
                # Create downloader object for compatibility
                downloader_obj = self
                self.downloader = type('obj', (object,), {
                    'channel_url': channel_url,
                    'download_path': download_path,
                    'videos': self.videos,
                    'filtered_videos': [],
                    'video_path': os.path.join(download_path, 'videos'),
                    'thumbnail_path': os.path.join(download_path, 'thumbnails'),
                    'sanitize_filename': lambda self, filename, max_length=100: downloader_obj.sanitize_filename(filename, max_length)
                })()
                
                # Create directories
                os.makedirs(self.downloader.video_path, exist_ok=True)
                os.makedirs(self.downloader.thumbnail_path, exist_ok=True)
                
                # Filter videos
                self.filter_videos()
                
                # Enable download button
                self.root.after(0, lambda: self.download_btn.config(state='normal'))
                
                return {'status': 'success'}
                
        except Exception as e:
            self.queue_log(f"❌ yt-dlp error: {str(e)}", 'error')
            import traceback
            self.queue_log(f"   Details: {traceback.format_exc()}", 'error')
            return {'status': 'error', 'message': str(e)}
    
    def remove_vietnamese_accents(self, text):
        """Remove Vietnamese diacritics/accents from text"""
        import unicodedata
        # Normalize to NFD (decomposed form) to separate base chars from accents
        nfd = unicodedata.normalize('NFD', text)
        # Filter out combining characters (accents)
        without_accents = ''.join(c for c in nfd if not unicodedata.combining(c))
        # Handle special Vietnamese characters
        replacements = {
            'đ': 'd', 'Đ': 'D',
            'ơ': 'o', 'Ơ': 'O',
            'ư': 'u', 'Ư': 'U',
        }
        for viet, latin in replacements.items():
            without_accents = without_accents.replace(viet, latin)
        return without_accents
    
    def sanitize_filename(self, filename, max_length=100):
        """Clean filename - remove special chars and Vietnamese accents"""
        import re
        # Remove Vietnamese accents first
        filename = self.remove_vietnamese_accents(filename)
        # Remove special characters, keep alphanumeric, spaces, and hyphens
        filename = re.sub(r'[^\w\s-]', '', filename)
        # Replace multiple spaces/hyphens with single space
        filename = re.sub(r'[-\s]+', ' ', filename)
        # Trim and limit length
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename.strip()
    
    def generate_filename(self, video_info, include_id=True, sequence_number=None):
        """Generate standardized filename with optional sequence number"""
        title = self.sanitize_filename(video_info['title'])
        
        # Add sequence number if provided
        if sequence_number is not None:
            prefix = f"{sequence_number:03d} "  # Format as 001, 002, 003...
        else:
            prefix = ""
        
        if include_id:
            return f"{prefix}{title} {video_info['video_id']}"
        return f"{prefix}{title}"
    
    def download_thumbnail_manual(self, video_info, sequence_number=None):
        """Download thumbnail manually in 16:9 aspect ratio with optional sequence number"""
        try:
            import urllib.request
            from PIL import Image, ImageOps
            
            thumbnail_urls = [
                f"https://img.youtube.com/vi/{video_info['video_id']}/maxresdefault.jpg",
                f"https://img.youtube.com/vi/{video_info['video_id']}/hqdefault.jpg",
                f"https://img.youtube.com/vi/{video_info['video_id']}/mqdefault.jpg",
            ]
            
            # Generate filename with sequence number (matching video filename)
            base_filename = self.generate_filename(video_info, include_id=True, sequence_number=sequence_number)
            thumbnail_filename = f"{base_filename}.jpg"
            full_path = os.path.join(self.downloader.thumbnail_path, thumbnail_filename)
            
            for url in thumbnail_urls:
                try:
                    urllib.request.urlretrieve(url, full_path)
                    img = Image.open(full_path)
                    img.verify()
                    img = Image.open(full_path)
                    
                    # Ensure 16:9 aspect ratio HD standard: 1280x720
                    target_width = 1280
                    target_height = 720  # 16:9 ratio (HD standard)
                    
                    # Get current dimensions
                    width, height = img.size
                    current_ratio = width / height
                    target_ratio = 16 / 9
                    
                    # Crop to 16:9 if needed
                    if abs(current_ratio - target_ratio) > 0.01:  # Not exactly 16:9
                        if current_ratio > target_ratio:
                            # Image is wider, crop width
                            new_width = int(height * target_ratio)
                            left = (width - new_width) // 2
                            img = img.crop((left, 0, left + new_width, height))
                        else:
                            # Image is taller, crop height
                            new_height = int(width / target_ratio)
                            top = (height - new_height) // 2
                            img = img.crop((0, top, width, top + new_height))
                    
                    # Resize to standard 16:9 dimensions
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    img.save(full_path, "JPEG", quality=90)
                    return full_path
                except:
                    continue
            return None
        except Exception as e:
            self.queue_log(f"   ⚠️ Thumbnail error: {str(e)}", 'warning')
            return None


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()