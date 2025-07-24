import os
import subprocess
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def is_yt_dlp_installed():
    try:
        import yt_dlp  # só importa para checar
        return True
    except ImportError:
        return False

def install_yt_dlp():
    app.logger.info("Instalando/atualizando yt-dlp...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'])
        app.logger.info("yt-dlp instalado com sucesso!")
    except Exception as e:
        app.logger.error(f"Erro ao instalar yt-dlp: {e}")

def get_video_formats(link):
    try:
        process = subprocess.Popen(['yt-dlp', '-F', link], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            app.logger.warning(f"Erro yt-dlp: {error.decode()}")
        return output.decode()
    except Exception as e:
        app.logger.error(f"Erro ao obter formatos: {e}")
        return None

def parse_formats(format_info):
    """
    Parse the yt-dlp -F output and extract all available formats in dict:
    { format_id: { 'ext': ext, 'resolution': res, 'fps': fps, 'note': note } }
    """
    formats = {}
    lines = format_info.splitlines()

    # Pula as primeiras linhas até achar header (geralmente começa com "format code")
    start_idx = 0
    for i, line in enumerate(lines):
        if line.lower().startswith("format code"):
            start_idx = i + 1
            break

    for line in lines[start_idx:]:
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        format_id = parts[0]
        ext = parts[1]
        resolution = parts[2]
        fps = None
        note = " ".join(parts[3:]) if len(parts) > 3 else ""

        # Se fps existe no note, tenta extrair (ex: "video only  1920x1080  30fps")
        if "fps" in note:
            try:
                fps_str = [p for p in note.split() if 'fps' in p][0]
                fps = int(fps_str.replace('fps',''))
            except:
                fps = None

        formats[format_id] = {
            'ext': ext,
            'resolution': resolution,
            'fps': fps,
            'note': note
        }
    return formats

def download(link, format_id):
    try:
        path_before = set(os.listdir(DOWNLOAD_FOLDER))
        # Forçar nome com título do vídeo + extensão correta
        process = subprocess.Popen([
            'yt-dlp', '-f', format_id,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            link
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            app.logger.error(f"Erro no download: {stderr.decode()}")
            return None, stderr.decode()

        path_after = set(os.listdir(DOWNLOAD_FOLDER))
        new_files = path_after - path_before
        downloaded_file = new_files.pop() if new_files else None

        return downloaded_file, None
    except Exception as e:
        app.logger.error(f"Erro no download: {e}")
        return None, str(e)

def download_audio(link):
    """Baixa o áudio padrão 140 (m4a)."""
    try:
        path_before = set(os.listdir(DOWNLOAD_FOLDER))
        process = subprocess.Popen([
            'yt-dlp', '-f', '140',
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s_audio.%(ext)s'),
            link
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            app.logger.error(f"Erro no download de áudio: {stderr.decode()}")
            return None, stderr.decode()

        path_after = set(os.listdir(DOWNLOAD_FOLDER))
        new_files = path_after - path_before
        downloaded_file = new_files.pop() if new_files else None
        return downloaded_file, None
    except Exception as e:
        app.logger.error(f"Erro no download de áudio: {e}")
        return None, str(e)

@app.route('/formats', methods=['POST'])
def formats():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    if not is_yt_dlp_installed():
        install_yt_dlp()

    info = get_video_formats(url)
    if not info:
        return jsonify({"error": "Não foi possível obter os formatos."}), 500

    parsed = parse_formats(info)
    return jsonify({"formats": parsed})

@app.route('/download', methods=['POST'])
def api_download():
    data = request.get_json()
    url = data.get('url')
    format_id = data.get('format_id')

    if not url or not format_id:
        return jsonify({"error": "Missing 'url' or 'format_id' parameter"}), 400

    if not is_yt_dlp_installed():
        install_yt_dlp()

    filename, error = download(url, format_id)
    if error:
        return jsonify({"error": error}), 500

    # Se formato é "video only", baixa áudio separado automaticamente
    info = get_video_formats(url)
    formats = parse_formats(info)
    note = formats.get(format_id, {}).get('note', '').lower()
    if 'video only' in note:
        audio_file, audio_error = download_audio(url)
        if audio_error:
            app.logger.warning(f"Erro ao baixar áudio separado: {audio_error}")

    return jsonify({"message": "Download concluído", "file": filename})

if __name__ == "__main__":
    app.logger.info("Iniciando API yt-dlp Flask")
    app.run(host="0.0.0.0", port=57342, debug=True)
