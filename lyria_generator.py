import os, base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

def get_api_key():
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")

def generar_audio_lyria(prompt_musical, modelo="lyria-3-clip-preview", formato="mp3", nombre="basa_track"):
    key = get_api_key()
    if not key:
        raise ValueError("Falta GEMINI_API_KEY en .env o en Streamlit Secrets.")
    client = genai.Client(api_key=key)
    kwargs = {"model": modelo, "input": prompt_musical}
    if modelo == "lyria-3.5" and formato == "wav":
        kwargs["response_format"] = {"type": "audio"}
    res = client.interactions.create(**kwargs)
    audio_bytes = None
    if getattr(res, "output_audio", None) and getattr(res.output_audio, "data", None):
        audio_bytes = base64.b64decode(res.output_audio.data)
    if not audio_bytes and getattr(res, "steps", None):
        for s in res.steps:
            if getattr(s, "type", "") == "model_output":
                for b in getattr(s, "content", []):
                    if getattr(b, "type", "") == "audio" and getattr(b, "data", None):
                        audio_bytes = base64.b64decode(b.data)
    if not audio_bytes:
        raise RuntimeError("La API no devolvio audio. Verifica permisos de Lyria 3.5 en tu API Key.")
    out_dir = BASE_DIR / "assets" / "audio_raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "wav" if (modelo == "lyria-3.5" and formato == "wav") else "mp3"
    ruta = out_dir / f"{nombre[:25]}_{stamp}.{ext}"
    ruta.write_bytes(audio_bytes)
    return {"ruta_audio": str(ruta), "letra": getattr(res, "output_text", "") or ""}
