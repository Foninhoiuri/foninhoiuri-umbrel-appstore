from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import re
import os
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

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
            app.logger.debug(f"matched regex search: {pattern}")
            return match.group(1)

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        return query['v'][0]

    return None

def sanitize_youtube_url(url):
    app.logger.debug(f"Sanitizing URL: {url}")
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Mantém só o parâmetro 'v' se existir, senão remove todos
    if 'v' in query:
        new_query = {'v': query['v'][0]}
    else:
        new_query = {}

    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(new_query),
        parsed.fragment
    ))
    app.logger.debug(f"Sanitized URL: {cleaned_url}")
    return cleaned_url

@app.route('/video_resolutions', methods=['POST'])
def video_resolutions():
    try:
        data = request.get_json()
        app.logger.info(f"Requisição recebida em /video_resolutions")
        app.logger.debug(f"Payload recebido: {data}")

        url = data.get('url')
        if not url:
            return jsonify({"error": "Missing 'url' parameter."}), 400

        url = sanitize_youtube_url(url)

        yt = YouTube(url)
        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        resolutions = sorted({stream.resolution for stream in video_streams if stream.resolution}, reverse=True)

        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        has_audio_only = len(audio_streams) > 0

        return jsonify({
            "resolutions": resolutions,
            "audio_only_available": has_audio_only,
            "title": yt.title
        }), 200

    except Exception as e:
        app.logger.error(f"Erro no endpoint /video_resolutions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        app.logger.info(f"Requisição recebida em /download")
        app.logger.debug(f"Payload recebido: {data}")

        url = data.get('url')
        choice = data.get('choice')  # ex: "720p", "360p", "audio"

        if not url or not choice:
            return jsonify({"error": "Missing 'url' or 'choice' parameter."}), 400

        url = sanitize_youtube_url(url)

        yt = YouTube(url)

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

        return jsonify({"message": f"Download concluído: {filename}", "filename": filename}), 200

    except Exception as e:
        app.logger.error(f"Erro no endpoint /download: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "Arquivo não encontrado."}), 404

if __name__ == '__main__':
    app.logger.info("Iniciando aplicação Flask")
    app.run(host='0.0.0.0', port=57342, debug=True)
