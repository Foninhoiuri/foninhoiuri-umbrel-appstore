# Use imagem oficial Python
FROM python:3.11-slim

# Cria pasta da app
WORKDIR /app

# Copia os arquivos da sua app
COPY . /app

# Instala as dependências (Flask, yt-dlp)
RUN pip install --no-cache-dir flask yt-dlp

# Expõe a porta que a app vai rodar
EXPOSE 57342

# Comando pra rodar sua aplicação Flask
CMD ["python", "app/main.py"]
