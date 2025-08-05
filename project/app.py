from flask import Flask, request, send_file, render_template_string
from yt_dlp import YoutubeDL
import os
import uuid
import tempfile

app = Flask(__name__)

# Read the HTML directly from the file in the same directory
def get_index_html():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        temp_dir = tempfile.gettempdir()
        filename = f"{uuid.uuid4()}.mp4"
        filepath = os.path.join(temp_dir, filename)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': filepath,
            'merge_output_format': 'mp4',
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True, download_name='video.mp4')

    return render_template_string(get_index_html())

if __name__ == '__main__':
    app.run(debug=True)
