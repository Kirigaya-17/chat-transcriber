from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from openai import OpenAI
import json
import wave
import tempfile
import os
import subprocess
from dotenv import load_dotenv

# --- Inicialização do app ---
app = FastAPI()
load_dotenv()  # carrega variáveis do .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- CORS para permitir o frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:5173"] para limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Carregar modelo Vosk ---
MODEL_PATH = "vosk-model-small-pt-0.3"
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        "Modelo Vosk não encontrado. Baixe e extraia antes de iniciar o servidor.")
model = Model(MODEL_PATH)


def convert_to_wav(input_path: str, output_path: str):
    """
    Converte qualquer arquivo de áudio (WebM, OGG, etc.)
    para WAV PCM 16kHz mono, usando ffmpeg.
    """
    cmd = [
        "ffmpeg",
        "-y",          # sobrescreve se já existir
        "-i", input_path,  # arquivo de entrada
        "-ac", "1",    # 1 canal (mono)
        "-ar", "16000",  # 16 kHz
        "-f", "wav",   # formato de saída
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Erro na conversão ffmpeg:", e.stderr.decode())
        raise RuntimeError("Falha na conversão do áudio para WAV.")


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile, format_text: bool = Form(True)):
    input_path = "temp_input.webm"
    output_path = "temp.wav"

    # Salva o arquivo temporariamente
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Converte para WAV PCM 16kHz mono
    convert_to_wav(input_path, output_path)

    # Processa o áudio com Vosk
    wf = wave.open(output_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "

    wf.close()

    # Garante que temos algum texto
    if not text.strip():
        return {"text": "Nenhum texto reconhecido."}

    # --- Formatação opcional com IA ---
    formatted_text = text

    # --- Retornar resultado ---
    return {"raw_text": text.strip(), "formatted_text": formatted_text}


# =============================
# EXECUÇÃO LOCAL
# =============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
