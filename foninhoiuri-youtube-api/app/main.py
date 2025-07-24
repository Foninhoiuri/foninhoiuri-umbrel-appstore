from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import re
import os
import logging
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configuração do logger para DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
)

def extract_video_id(url):
    logging.debug(f"Tentando extrair video_id da URL: {url}")
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
            video_id = match.group(1)
            logging.debug(f"Video ID encontrado via regex: {video_id}")
            return video_id

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        video_id = query['v'][0]
        logging.debug(f"Video ID encontrado via query string: {video_id}")
        return video_id

    logging.warning("Não foi possível extrair video_id da URL")
    return None

def get_video_info(url):
    logging.debug(f"Obtendo informações do vídeo para URL: {url}")
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
        logging.debug(f"Informações do vídeo obtidas com sucesso: {video_info}")
        return video_info, None
    except Exception as e:
        logging.error(f"Erro ao obter informações do vídeo: {e}")
        return None, str(e)

@app.route('/video_resolutions', methods=['POST'])
def video_resolutions():
    logging.info("Requisição recebida em /video_resolutions")
    data = request.get_json()
    logging.debug(f"Payload recebido: {data}")
    url = data.get('url')

    if not url:
        logging.warning("Faltando parâmetro 'url' no corpo da requisição")
        return jsonify({"error": "Missing 'url' parameter."}), 400
    
    try:
        yt = YouTube(url)
        # Resoluções progressivas (vídeo+áudio)
        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        resolutions = sorted({stream.resolution for stream in video_streams if stream.resolution}, reverse=True)
        
        # Checar se tem áudio-only
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        has_audio_only = len(audio_streams) > 0

        response = {
            "resolutions": resolutions,
            "audio_only_available": has_audio_only,
            "title": yt.title
        }
        logging.info(f"Resoluções encontradas: {response}")
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Erro no endpoint /video_resolutions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    logging.info("Requisição recebida em /download")
    data = request.get_json()
    logging.debug(f"Payload recebido: {data}")
    url = data.get('url')
    choice = data.get('choice')  # ex: "720p", "360p" ou "audio"

    if not url or not choice:
        logging.warning("Faltando parâmetro 'url' ou 'choice' no corpo da requisição")
        return jsonify({"error": "Missing 'url' or 'choice' parameter."}), 400
    
    try:
        yt = YouTube(url)

        filename = None

        if choice == "audio":
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if not audio_stream:
                logging.warning("Nenhum stream de áudio-only disponível")
                return jsonify({"error": "No audio-only stream available."}), 404
            filename = audio_stream.default_filename
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            logging.info(f"Baixando áudio: {filename}")
            audio_stream.download(output_path=DOWNLOAD_FOLDER)
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=choice).first()
            if not video_stream:
                logging.warning(f"Nenhum stream de vídeo encontrado com resolução {choice}")
                return jsonify({"error": f"No video stream found with resolution {choice}."}), 404
            filename = video_stream.default_filename
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            logging.info(f"Baixando vídeo: {filename} na resolução {choice}")
            video_stream.download(output_path=DOWNLOAD_FOLDER)
        
        logging.info(f"Download concluído: {filename}")
        return jsonify({"message": f"Download concluído: {filename}", "filename": filename}), 200

    except Exception as e:
        logging.error(f"Erro no endpoint /download: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    logging.info(f"Requisição para baixar arquivo: {filename}")
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        logging.info(f"Arquivo encontrado: {filename}, enviando para cliente")
        return send_file(path, as_attachment=True)
    else:
        logging.warning(f"Arquivo não encontrado: {filename}")
        return jsonify({"error": "Arquivo não encontrado."}), 404

if __name__ == '__main__':
    logging.info("Iniciando aplicação Flask")
    app.run(host='0.0.0.0', port=57342, debug=True)
