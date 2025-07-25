# Usa imagem oficial Python slim
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copia requirements (se houver) e depois o código
# Como você não tem requirements.txt, vamos instalar direto no Dockerfile

# Instala dependências do sistema necessárias (ex: ffmpeg para yt-dlp funcionar corretamente)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copia o código da aplicação para /app
COPY . /app

# Instala o Flask e yt-dlp via pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask yt-dlp

# Expõe a porta que a API Flask usará
EXPOSE 57342

# Comando para rodar a aplicação Flask
CMD ["python", "main.py"]
