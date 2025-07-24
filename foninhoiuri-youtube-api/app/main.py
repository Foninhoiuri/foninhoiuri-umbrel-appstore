from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import re
import os
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        return query['v'][0]

    return None

def get_video_info(url):
    try:
        yt = YouTube(url)
        video_info = {
            "videoId": extract_video_id(url),
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date.isoformat() if yt.publish_date else None,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

@app.route('/video_resolutions', methods=['POST'])
def video_resolutions():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing 'url' parameter."}), 400
    
    try:
        yt = YouTube(url)
        # Resoluções progressivas (vídeo+áudio)
        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        resolutions = sorted({stream.resolution for stream in video_streams if stream.resolution}, reverse=True)
        
        # Checar se tem áudio-only
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        has_audio_only = len(audio_streams) > 0

        return jsonify({
            "resolutions": resolutions,
            "audio_only_available": has_audio_only,
            "title": yt.title
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    choice = data.get('choice')  # ex: "720p", "360p" ou "audio"

    if not url or not choice:
        return jsonify({"error": "Missing 'url' or 'choice' parameter."}), 400
    
    try:
        yt = YouTube(url)

        filename = None

        if choice == "audio":
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if not audio_stream:
                return jsonify({"error": "No audio-only stream available."}), 404
            filename = audio_stream.default_filename
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            audio_stream.download(output_path=DOWNLOAD_FOLDER)
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=choice).first()
            if not video_stream:
                return jsonify({"error": f"No video stream found with resolution {choice}."}), 404
            filename = video_stream.default_filename
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            video_stream.download(output_path=DOWNLOAD_FOLDER)
        
        # Aqui poderia enviar o arquivo direto, mas para não travar, só retorna o nome
        return jsonify({"message": f"Download concluído: {filename}", "filename": filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Opcional: rota para baixar o arquivo pelo nome (se quiser expor isso)
@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "Arquivo não encontrado."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=57342, debug=True)
