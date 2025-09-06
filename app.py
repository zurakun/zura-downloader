# File: app.py (Versi Baru untuk MP3 & MP4 + Proxy + Auto Remove WM)

from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import subprocess

app = Flask(__name__)
TEMP_DIR = "temp_downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Proxy (ubah di sini kalau proxy baru)
PROXY = "http://128.199.202.122:8080"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getinfo', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'proxy': PROXY
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            audio_formats = []
            
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'resolution': f.get('resolution'),
                        'filesize_human': f.get('filesize_approx_str') or 'N/A'
                    })
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_formats.append(f)

            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0), default=None)
            
            return jsonify({
                'title': info.get('title', 'No title'),
                'video_formats': formats,
                'best_audio_id': best_audio.get('format_id') if best_audio else None
            })
    except Exception as e:
        return jsonify({'error': f"Gagal mengambil info: {str(e)}"}), 500

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    dl_type = request.args.get('type', 'video')

    if not url or not format_id:
        return "URL atau Format ID tidak ada.", 400

    try:
        if dl_type == 'audio':
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'proxy': PROXY,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename = os.path.splitext(filename)[0] + '.mp3'

            return send_file(filename, as_attachment=True)

        else:  # Tipe video
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'proxy': PROXY
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Buat file baru hasil filter tanpa watermark
            clean_filename = os.path.splitext(filename)[0] + "_clean.mp4"

            # FFmpeg delogo (posisi WM: x=10, y=10, w=150, h=50)
            subprocess.run([
                "ffmpeg", "-y", "-i", filename,
                "-vf", "delogo=x=10:y=10:w=150:h=50:show=0",
                "-c:a", "copy", clean_filename
            ])

            return send_file(clean_filename, as_attachment=True)

    except Exception as e:
        return f"Terjadi error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
