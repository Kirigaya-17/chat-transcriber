from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from openai import OpenAI
import json
import wave
import tempfile
import os
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


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile, format_text: bool = Form(True)):
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_bytes = await file.read()
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    # Converter para WAV PCM 16kHz mono (compatível com Vosk)
    wav_path = tempfile.mktemp(suffix=".wav")
    try:
        audio = AudioSegment.from_file(temp_audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")
    except Exception as e:
        return {"error": f"Erro ao converter áudio: {str(e)}"}

    # --- Transcrição com Vosk ---
    rec = KaldiRecognizer(model, 16000)
    text = ""
    with wave.open(wav_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get("text", "") + " "
        final = json.loads(rec.FinalResult())
        text += final.get("text", "")

    print('Text:', text)

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
