import sqlite3, hashlib
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "basa_music.db"

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    (BASE_DIR / "assets" / "audio_raw").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "assets" / "audio_exports").mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS canciones (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, autor TEXT, genero TEXT, bpm INTEGER, letra TEXT, ruta_audio TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        c.commit()

def guardar_tema(titulo, autor, genero, bpm, letra, ruta_audio=""):
    with _conn() as c:
        cur = c.execute("INSERT INTO canciones (titulo, autor, genero, bpm, letra, ruta_audio) VALUES (?,?,?,?,?,?)", (titulo, autor, genero, bpm, letra, ruta_audio))
        c.commit()
        return cur.lastrowid

def listar_temas():
    with _conn() as c:
        return pd.read_sql_query("SELECT * FROM canciones ORDER BY id DESC", c)
