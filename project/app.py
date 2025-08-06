from flask import Flask, request, send_file, render_template
import yt_dlp
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")  # Make sure index.html exists in /templates/

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    itag = request.form.get('itag')

    if not url or not itag:
        return "Missing URL or itag", 400

    # Temp download path
    temp_dir = tempfile.gettempdir()

    ydl_opts = {
        'format': f'{itag}+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Error downloading video: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
