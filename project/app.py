from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import yt_dlp
import tempfile
import os
import re
import mysql.connector
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import bcrypt

app = Flask(__name__)
# NOTE: Use a stable secret in production; os.urandom resets sessions on every restart.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Database configuration
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),  # XAMPP default is empty
    'database': os.environ.get('DB_NAME', 'youtube_downloader')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            video_title VARCHAR(255) NOT NULL,
            video_url TEXT NOT NULL,
            quality VARCHAR(20) NOT NULL,
            download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create a default admin if none exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
    if cursor.fetchone()[0] == 0:
        admin_password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            ('admin', admin_password_hash, True)
        )

    conn.commit()
    cursor.close()
    conn.close()

# Initialize database
init_db()

# ---------- Auth helpers ----------

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT is_admin FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user or not user['is_admin']:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapped

# ---------- Public / protected routing policy ----------
@app.before_request
def open_routes_allowlist():
    """
    Keep these endpoints public (no login required).
    Everything else uses explicit @login_required / @admin_required where needed.
    """
    public_endpoints = {
        'index', 'about', 'login', 'register', 'info', 'logout', 'static'
    }
    if request.endpoint is None:
        return
    if request.endpoint in public_endpoints:
        return
    
# ---------- Validators ----------

def is_valid_username(username):
    """Validate username format (alphanumeric/underscore, 3-20 chars)"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username or "") is not None

def is_valid_password(password):
    """Validate password (at least 6 characters)"""
    return isinstance(password, str) and len(password) >= 6

def is_valid_youtube_url(url):
    """Validate if the URL is a valid YouTube URL"""
    url = (url or "").strip()
    youtube_regex = (
        r'^(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    if re.match(youtube_regex, url):
        return True
    if url.startswith(('https://youtu.be/', 'http://youtu.be/')):
        return True
    return False

# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html", username=session.get('username'))

@app.route("/about")
def about():
    return render_template("about.html", username=session.get('username'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""
        errors = []

        if not username or not password or not confirm_password:
            errors.append("All fields are required.")
        if not is_valid_username(username):
            errors.append("Username must be 3-20 characters and can only contain letters, numbers, and underscores.")
        if not is_valid_password(password):
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            return render_template("register.html", errors=errors, username=username)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template("register.html", errors=["Username already exists."], username=username)

        # Store bcrypt hash as UTF-8 string
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()

        # Get user ID for session
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        session['username'] = username
        session['is_admin'] = False
        session['user_id'] = user['id']

        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # user['password'] is stored as UTF-8 string; encode before check
        if user and bcrypt.checkpw(password.encode('utf-8'), (user['password'] or "").encode('utf-8')):
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            session['user_id'] = int(user['id'])
            return redirect(url_for('index'))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/history")
@login_required
def history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT video_title, quality, download_date
        FROM downloads
        WHERE user_id = %s
        ORDER BY download_date DESC
    """, (session['user_id'],))
    downloads = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("history.html", username=session.get('username'), downloads=downloads)

@app.route("/admin")
@admin_required
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_downloads FROM downloads")
    total_downloads = cursor.fetchone()['total_downloads']

    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("""
        SELECT u.username AS user, d.video_title, d.download_date
        FROM downloads d
        JOIN users u ON d.user_id = u.id
        ORDER BY d.download_date DESC
        LIMIT 10
    """)
    recent_downloads = cursor.fetchall()

    cursor.execute("""
        SELECT u.id, u.username, COUNT(d.id) AS download_count, u.is_admin
        FROM users u
        LEFT JOIN downloads d ON u.id = d.user_id
        GROUP BY u.id
    """)
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    stats = {
        'total_downloads': total_downloads,
        'total_users': total_users,
        'recent_downloads': recent_downloads
    }

    return render_template("admin.html", username=session.get('username'), stats=stats, users=users)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    # Don't allow deleting yourself
    if user_id == session.get('user_id'):
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin'))

# ---------- Public INFO endpoint (no login required) ----------

@app.route("/info", methods=["POST"])
def info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": f"yt-dlp error: {e}"}), 400

    if "entries" in info and info["entries"]:
        info = info["entries"][0]

    formats = info.get("formats", []) or []

    def is_video_capable(f):
        return (f.get("vcodec") not in (None, "none"))

    reduced = []
    seen_keys = set()
    for f in formats:
        if not is_video_capable(f):
            continue
        key = (f.get("height") or 0, f.get("vcodec"), f.get("ext"))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        reduced.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "height": f.get("height"),
            "width": f.get("width"),
            "fps": f.get("fps"),
            "tbr": f.get("tbr"),
            "format_note": f.get("format_note"),
            "acodec": f.get("acodec"),
            "vcodec": f.get("vcodec"),
            # ✅ Always treat as has_audio, since we merge bestaudio
            "has_audio": True,
        })

    reduced.sort(key=lambda f: ((f["height"] or 0), (f["tbr"] or 0)), reverse=True)

    return jsonify({
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "video_formats": reduced,
    })

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    format_id = (data.get("format_id") or "").strip()
    if not url or not format_id:
        return jsonify({"error": "Missing URL or format_id"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": f"yt-dlp error: {e}"}), 400

    if "entries" in info and info["entries"]:
        info = info["entries"][0]

    selected = None
    for f in (info.get("formats") or []):
        if f.get("format_id") == format_id:
            selected = f
            break

    if not selected:
        return jsonify({"error": "Selected format not found"}), 400

    has_video = (selected.get("vcodec") not in (None, "none"))
    if not has_video:
        return jsonify({"error": "Chosen format is not a video format"}), 400

    fmt_str = f"{format_id}+bestaudio/best"

    tmpdir = tempfile.mkdtemp(prefix="ytmp4_")
    outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": fmt_str,
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            finfo = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(finfo)
    except Exception as e:
        return jsonify({"error": f"yt-dlp download error: {e}"}), 500

    base, _ = os.path.splitext(filepath)
    mp4_path = base + ".mp4"
    final_path = mp4_path if os.path.exists(mp4_path) else filepath

    # Record download in database only if logged in
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO downloads (user_id, video_title, video_url, quality) VALUES (%s, %s, %s, %s)",
                (session['user_id'], finfo.get('title'), url, f"{selected.get('height', '')}p")
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    safe_name = secure_filename(os.path.basename(final_path)) or "video.mp4"
    return send_file(final_path, as_attachment=True, download_name=safe_name)

if __name__ == "__main__":
    # In production, set host/port via env and disable debug
    app.run(debug=True)
