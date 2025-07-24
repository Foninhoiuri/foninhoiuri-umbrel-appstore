from flask import Flask, request, jsonify
import yt_dlp
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Extrai ID do YouTube igual ao seu
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
    ydl_opts = {}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = {
                "videoId": extract_video_id(url),
                "title": info.get('title'),
                "uploader": info.get('uploader'),
                "duration": info.get('duration'),
                "view_count": info.get('view_count'),
                "description": info.get('description'),
                "upload_date": info.get('upload_date'),
                "webpage_url": info.get('webpage_url'),
            }
            return video_info, None
    except Exception as e:
        return None, str(e)

def download_video(url, resolution):
    # yt-dlp não filtra direto por resolução como pytube, mas podemos passar opções para formatos
    ydl_opts = {
        'format': f'bestvideo[height<={resolution.rstrip("p")}]+bestaudio/best[height<={resolution.rstrip("p")}]',
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, None
    except Exception as e:
        return False, str(e)

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter."}), 400
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL."}), 400
    info, err = get_video_info(url)
    if info:
        return jsonify(info), 200
    else:
        return jsonify({"error": err}), 500

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter."}), 400
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL."}), 400
    success, err = download_video(url, resolution)
    if success:
        return jsonify({"message": f"Video downloaded in up to {resolution} resolution."}), 200
    else:
        return jsonify({"error": err}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=57342, debug=True)
