import streamlit as st
from pathlib import Path
from db_manager import init_db, guardar_tema, listar_temas
from lyria_generator import generar_audio_lyria

st.set_page_config(page_title="BASA Music Studio Pro", page_icon="🎵", layout="wide")
init_db()

st.title("🎵 BASA Music Studio Pro · Lyria 3.5 & Suno Style")
st.caption("Generacion musical profesional en la nube · Listo para Streamlit Cloud")

GENEROS = ["Merengue Tipico (Perico Ripiao)", "Merengue de Calle", "Bachata", "Salsa", "Dembow / Urbano", "Ranchera / Mariachi", "Afrobeat / Funk", "Bolero / Balada"]

tab1, tab2 = st.tabs(["🎹 Crear Musica (Lyria 3.5)", "📚 Biblioteca"])

with tab1:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        titulo = st.text_input("Titulo del tema", placeholder="Ej. Amanecer en el Caribe")
        autor = st.text_input("Autor", value="Pedro Baldera (BASA66)")
        g_col, m_col = st.columns(2)
        genero = g_col.selectbox("Genero", GENEROS)
        modelo = m_col.selectbox("Motor Lyria", ["lyria-3-clip-preview", "lyria-3.5"])
        b_col, f_col, i_col = st.columns(3)
        bpm = b_col.number_input("BPM", 60, 220, 135)
        fmt = f_col.selectbox("Formato", ["mp3", "wav"])
        inst = i_col.checkbox("Solo Instrumental")
        idea = st.text_area("Letra ([Verse], [Chorus]) o descripcion musical", height=160)
        if st.button("🎵 Generar Audio Ahora", type="primary", use_container_width=True):
            if not idea.strip():
                st.warning("Escribe una letra o descripcion primero.")
            else:
                try:
                    prompt = f"Estilo {genero}, {bpm} BPM. {'Instrumental only, no vocals.' if inst else ''} {idea}"
                    with st.spinner("Sintetizando audio con Google Lyria..."):
                        out = generar_audio_lyria(prompt, modelo, fmt, titulo or "tema_basa")
                    st.session_state["ultimo_audio"] = out
                    guardar_tema(titulo or "Sin titulo", autor, genero, bpm, out["letra"] or idea, out["ruta_audio"])
                    st.success("Audio generado y guardado!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with c2:
        st.subheader("Reproductor")
        ult = st.session_state.get("ultimo_audio")
        if ult and Path(ult["ruta_audio"]).exists():
            st.audio(ult["ruta_audio"])
            st.download_button("⬇️ Descargar Audio", data=Path(ult["ruta_audio"]).read_bytes(), file_name=Path(ult["ruta_audio"]).name, use_container_width=True)
            if ult.get("letra"):
                st.text_area("Letra / Estructura", ult["letra"], height=180)
        else:
            st.info("Genera una pista para escucharla y descargarla aqui.")

with tab2:
    df = listar_temas()
    if df.empty:
        st.info("Aun no hay temas guardados.")
    else:
        st.dataframe(df[["id", "titulo", "autor", "genero", "bpm", "fecha"]], use_container_width=True, hide_index=True)
