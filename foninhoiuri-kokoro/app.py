# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import io
import numpy as np # Adicionado para concatenação de áudio
import soundfile as sf
import sys

# Tente importar KPipeline. Se falhar, é provável que as dependências não estejam instaladas.
try:
    from kokoro import KPipeline
except ImportError:
    print("A biblioteca Kokoro não foi encontrada. Certifique-se de que está instalada e que o espeak-ng está disponível.", file=sys.stderr)
    sys.exit(1) # Saia se a biblioteca essencial não estiver presente

app = FastAPI(
    title="Kokoro TTS API Personalizada",
    description="API para conversão de texto em fala usando a biblioteca Kokoro com opções avançadas."
)

class TTSRequest(BaseModel):
    text: str
    lang_code: str = 'a' # Código do idioma (ex: 'a' para American English, 'p' para Brazilian Portuguese)
    voice: str = 'af_heart' # Nome da voz (verifique as vozes disponíveis na documentação do Kokoro)
    speed: float = 1.0 # Velocidade da fala (1.0 é normal)
    split_pattern: str = r'\n+' # Padrão regex para dividir o texto em frases

@app.post("/tts")
async def generate_tts(request: TTSRequest):
    try:
        # ATENÇÃO: Instanciar KPipeline para cada requisição com um 'lang_code' diferente
        # pode ser lento e consumir muita memória. Para uso em produção, considere
        # carregar e cachear as instâncias de KPipeline para os idiomas mais usados.
        pipeline = KPipeline(lang_code=request.lang_code)

        generator = pipeline(
            request.text,
            voice=request.voice,
            speed=request.speed,
            split_pattern=request.split_pattern
        )

        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_segments.append(audio)

        if not audio_segments:
            raise HTTPException(status_code=500, detail="Falha ao gerar segmentos de áudio.")

        # Concatena todos os arrays de áudio em um único array NumPy
        full_audio_array = np.concatenate(audio_segments)

        # Escreve o áudio completo em um buffer de memória
        output_buffer = io.BytesIO()
        sf.write(output_buffer, full_audio_array, 24000, format='WAV') # Taxa de amostragem padrão de 24000
        output_buffer.seek(0) # Volta o ponteiro para o início do buffer

        return StreamingResponse(output_buffer, media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração de TTS: {str(e)}. Verifique os logs do contêiner.")

@app.get("/")
async def root():
    return {"message": "API Kokoro TTS Personalizada está funcionando. Use /tts para conversão de texto em fala."}
