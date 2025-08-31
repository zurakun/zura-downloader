# File: app.py (Versi Baru untuk MP3 & MP4)

from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)
TEMP_DIR = "temp_downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getinfo', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400

    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            audio_formats = []
            
            for f in info.get('formats', []):
                # Opsi Video (MP4 dengan video & audio)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'resolution': f.get('resolution'),
                        'filesize_human': f.get('filesize_approx_str') or 'N/A'
                    })
                # Opsi Audio terbaik (untuk konversi MP3)
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_formats.append(f)

            # Cari audio dengan kualitas terbaik untuk dijadikan MP3
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
            # Opsi untuk ekstrak audio ke MP3
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192', # Kualitas MP3 192kbps
                }],
            }
        else: # Tipe video
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Jika audio, nama file diubah dari .webm/.m4a menjadi .mp3
            if dl_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Terjadi error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)