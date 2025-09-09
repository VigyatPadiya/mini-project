YouTube Video Downloader - Installation and Setup Guide

Overview

A Flask-based web application for downloading YouTube videos in various
formats with user authentication and download history tracking.

Prerequisites

-   Python 3.7 or higher
-   MySQL Server 5.7 or higher
-   FFmpeg (for video processing)
-   VLC Media Player (recommended for optimal playback)

Installation Steps

1. Install Python Dependencies

    pip install flask yt-dlp mysql-connector-python bcrypt werkzeug

2. Install FFmpeg

-   Windows: Download from https://ffmpeg.org/download.html and add to
    PATH
-   macOS: brew install ffmpeg
-   Linux (Ubuntu/Debian): sudo apt install ffmpeg

3. Install VLC Media Player (Recommended)

-   Download from https://www.videolan.org/vlc/

4. Database Setup

1.  Start your MySQL server
2.  Run the database setup script:

    python setup_database.py

This will: - Create the youtube_downloader database - Create necessary
tables (users, downloads) - Add default admin user (admin/admin123) and
test user (user/user123)

5. Configure Environment Variables (Optional)

Set these environment variables if you need to customize the database
connection:

    export DB_HOST=localhost
    export DB_USER=root
    export DB_PASSWORD=your_password
    export DB_NAME=youtube_downloader
    export FLASK_SECRET_KEY=your_secret_key

6. Run the Application

    python app.py

7. Access the Application

Open your web browser and navigate to:

    http://localhost:5000

Default Login Credentials

-   Admin: username admin, password admin123
-   Test User: username user, password user123

Usage Instructions

1.  Home Page: Paste a YouTube URL and click “Fetch Video”
2.  Registration: Create a new account to track your download history
3.  Login: Access your download history and user features
4.  Download: Select your desired quality and download the video
5.  History: View your download history (requires login)
6.  Admin Panel: Access user management and statistics (admin only)

Troubleshooting

Common Issues

1.  MySQL Connection Error
    -   Ensure MySQL server is running
    -   Verify database credentials in app.py
2.  Video Download Fails
    -   Check internet connection
    -   Verify YouTube URL is valid
3.  FFmpeg Not Found
    -   Ensure FFmpeg is installed and in system PATH
4.  VLC Playback Issues
    -   Update VLC to the latest version
    -   Install necessary codecs

Getting Help

If you encounter issues: 1. Check that all dependencies are installed
correctly 2. Verify database connection settings 3. Ensure required
ports (5000 for Flask, 3306 for MySQL) are available

Notes

-   Downloaded files are temporary and removed after download
-   For optimal playback experience, use VLC Media Player
-   The application is designed for personal use only
-   Respect copyright laws when downloading content

License

This project is for educational purposes. Please ensure you comply with
YouTube’s Terms of Service when using this application.
