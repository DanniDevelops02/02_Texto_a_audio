import base64
import io
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from PIL import Image

st.set_page_config(
    page_title="Texto a Audio · Daniel Flórez",
    page_icon="🎧",
    layout="centered",
)

# =====================================================================
#  CONTENIDO
# =====================================================================
IMAGEN = "gato_raton.png"

FABULA = (
    "¡Ay! —dijo el ratón—. El mundo se hace cada día más pequeño. Al principio "
    "era tan grande que le tenía miedo. Corría y corría y por cierto que me "
    "alegraba ver esos muros, a diestra y siniestra, en la distancia. Pero esas "
    "paredes se estrechan tan rápido que me encuentro en el último cuarto y ahí "
    "en el rincón está la trampa sobre la cual debo pasar. Todo lo que debes "
    "hacer es cambiar de rumbo —dijo el gato... y se lo comió."
)
AUTOR_FABULA = "Franz Kafka"

IDIOMAS = {
    "Español": "es",
    "English": "en",
    "Français": "fr",
    "Português": "pt",
    "Italiano": "it",
}

# =====================================================================
#  ESTILO (paleta fría basada en #3f71a6)
# =====================================================================
PRIMARIO = "#3f71a6"
OSCURO = "#1b2f45"
CLARO = "#eaf2f9"
SUAVE = "#a9c7e3"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif;
        font-size: 1.08rem;
    }}
    .stApp {{
        background: linear-gradient(180deg, #f6fafd 0%, {CLARO} 100%);
    }}
    .block-container {{
        max-width: 860px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }}

    /* Hero */
    .hero {{ text-align: center; padding: 1rem 0 .5rem 0; }}
    .hero .etiqueta {{
        color: {PRIMARIO};
        letter-spacing: .25em;
        text-transform: uppercase;
        font-size: .85rem;
        font-weight: 600;
    }}
    .hero h1 {{
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        color: {OSCURO};
        margin: .3rem 0 .6rem 0;
        line-height: 1.1;
    }}
    .hero p {{
        color: #4d6479;
        font-size: 1.2rem;
        max-width: 620px;
        margin: 0 auto;
    }}
    .linea {{
        width: 70px; height: 4px; border-radius: 4px;
        background: {PRIMARIO};
        margin: 1.4rem auto;
    }}

    h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: {OSCURO} !important;
    }}

    /* Tarjetas */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: white;
        border: 1px solid {SUAVE}66 !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 24px rgba(63, 113, 166, .08);
        padding: .6rem .8rem;
    }}

    /* Imagen grande (cambia 2 / 1 por 16 / 9 para hacerla más alta) */
    [data-testid="stImage"] img {{
        width: 100%;
        aspect-ratio: 2 / 1;
        object-fit: cover;
        border-radius: 20px;
        box-shadow: 0 12px 32px rgba(27, 47, 69, .18);
    }}

    /* Fábula */
    .fabula {{
        background: white;
        border-left: 5px solid {PRIMARIO};
        border-radius: 0 18px 18px 0;
        padding: 1.5rem 1.7rem;
        box-shadow: 0 8px 24px rgba(63, 113, 166, .08);
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        line-height: 1.75;
        color: {OSCURO};
    }}
    .fabula .autor {{
        margin-top: .9rem;
        font-family: 'Inter', sans-serif;
        font-size: .85rem;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: {PRIMARIO};
    }}

    /* Botones */
    .stButton > button, .stDownloadButton > button {{
        background: {PRIMARIO};
        color: white;
        border: 1.5px solid {PRIMARIO};
        border-radius: 999px;
        padding: .7rem 1.6rem;
        font-size: 1.02rem;
        font-weight: 600;
        transition: all .2s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: {OSCURO};
        border-color: {OSCURO};
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(27, 47, 69, .25);
    }}
    [data-testid="stBaseButton-secondary"] {{
        background: white;
        color: {PRIMARIO};
    }}

    /* Inputs */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
        border-radius: 12px;
        border: 1px solid {SUAVE};
        font-size: 1.05rem;
    }}
    [data-testid="stAlert"] {{ border-radius: 14px; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{ background: {OSCURO}; }}
    [data-testid="stSidebar"] * {{ color: #e6f0f9 !important; }}

    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
#  REPRODUCTOR CON ONDA DE SONIDO (HTML + JavaScript)
# =====================================================================
PLAYER_HTML = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: transparent; }
  .player { display: flex; align-items: center; gap: 18px; padding: 8px 2px; }
  .play {
    width: 66px; height: 66px; border-radius: 50%; border: none; flex: none;
    background: __PRIMARIO__; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background .2s ease, transform .2s ease;
  }
  .play:hover { background: __OSCURO__; transform: scale(1.06); }
  .play svg { width: 28px; height: 28px; fill: white; }
  .wave { flex: 1; height: 88px; display: flex; align-items: center; gap: 3px; cursor: pointer; }
  .bar { flex: 1; min-width: 2px; border-radius: 3px; background: __SUAVE__; transition: background .15s; }
  .bar.done { background: __PRIMARIO__; }
  .time { min-width: 92px; text-align: right; font-size: .9rem; color: #4d6479;
          font-variant-numeric: tabular-nums; }
</style>

<div class="player">
  <button class="play" id="btn" aria-label="Reproducir o pausar">
    <svg viewBox="0 0 24 24"><path id="icon" d="M8 5v14l11-7z"/></svg>
  </button>
  <div class="wave" id="wave" title="Haz clic para saltar a otro punto"></div>
  <div class="time" id="time">0:00 / 0:00</div>
</div>
<audio id="audio" preload="auto" src="data:audio/mpeg;base64,__AUDIO__"></audio>

<script>
  const N = 56;
  const PLAY = "M8 5v14l11-7z";
  const PAUSE = "M6 5h4v14H6zM14 5h4v14h-4z";
  const audio = document.getElementById("audio");
  const wave = document.getElementById("wave");
  const btn = document.getElementById("btn");
  const icon = document.getElementById("icon");
  const time = document.getElementById("time");

  // Forma base de la onda (fija, para que siempre se vea igual)
  const base = Array.from({length: N}, (_, i) =>
    0.22 + 0.78 * Math.abs(Math.sin(i * 0.9) * Math.cos(i * 0.37)));
  const bars = base.map(() => {
    const d = document.createElement("div");
    d.className = "bar";
    wave.appendChild(d);
    return d;
  });

  let playing = false;

  function fmt(s) {
    if (!isFinite(s)) return "0:00";
    const m = Math.floor(s / 60), r = Math.floor(s % 60);
    return m + ":" + String(r).padStart(2, "0");
  }

  function draw(t) {
    const dur = isFinite(audio.duration) ? audio.duration : 0;
    const p = dur ? audio.currentTime / dur : 0;
    bars.forEach((b, i) => {
      const wob = playing ? 0.68 + 0.32 * Math.sin(t / 130 + i * 0.7) : 1;
      b.style.height = (base[i] * wob * 100) + "%";
      b.classList.toggle("done", i / N < p);
    });
    time.textContent = fmt(audio.currentTime) + " / " + fmt(dur);
    if (playing) requestAnimationFrame(draw);
  }

  btn.onclick = () => (audio.paused ? audio.play() : audio.pause());

  audio.addEventListener("play", () => {
    playing = true;
    icon.setAttribute("d", PAUSE);
    requestAnimationFrame(draw);
  });
  const detener = () => {
    playing = false;
    icon.setAttribute("d", PLAY);
    draw(0);
  };
  audio.addEventListener("pause", detener);
  audio.addEventListener("ended", detener);
  audio.addEventListener("loadedmetadata", () => draw(0));

  wave.addEventListener("click", (e) => {
    const r = wave.getBoundingClientRect();
    if (isFinite(audio.duration)) {
      audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
      if (!playing) draw(0);
    }
  });

  draw(0);
</script>
"""


def reproductor(audio_bytes: bytes) -> str:
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return (
        PLAYER_HTML.replace("__AUDIO__", audio_b64)
        .replace("__PRIMARIO__", PRIMARIO)
        .replace("__OSCURO__", OSCURO)
        .replace("__SUAVE__", SUAVE)
    )


# =====================================================================
#  LÓGICA
# =====================================================================
BASE = Path(__file__).parent


def generar_audio(texto: str, idioma: str, lento: bool) -> bytes:
    buffer = io.BytesIO()
    gTTS(texto, lang=idioma, slow=lento).write_to_fp(buffer)
    return buffer.getvalue()


def usar_fabula():
    st.session_state["texto"] = FABULA


# =====================================================================
#  PÁGINA
# =====================================================================
with st.sidebar:
    st.subheader("Cómo usarlo")
    st.markdown(
        "1. Escribe o pega el texto que quieres escuchar.\n"
        "2. Elige el idioma.\n"
        "3. Pulsa **Convertir a audio** y dale al play."
    )

st.markdown(
    """
    <div class="hero">
        <div class="etiqueta">Texto a voz</div>
        <h1>Conversión de texto a audio</h1>
        <p>Escribe o pega un texto y escúchalo en el idioma que prefieras.</p>
        <div class="linea"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

ruta_imagen = BASE / IMAGEN
if ruta_imagen.is_file():
    st.image(Image.open(ruta_imagen), use_container_width=True)
else:
    st.info(f"Agrega la imagen '{IMAGEN}' al repositorio para verla aquí.")

st.write("")

st.markdown(
    f"""
    <div class="fabula">
        {FABULA}
        <div class="autor">{AUTOR_FABULA} · Una pequeña fábula</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.container(border=True):
    st.subheader("Tu texto")
    texto = st.text_area(
        "Texto a escuchar",
        key="texto",
        height=170,
        placeholder="Escribe o pega aquí el texto que quieres escuchar...",
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
    with c1:
        idioma_nombre = st.selectbox("Idioma", list(IDIOMAS))
    with c2:
        lento = st.toggle("Voz lenta")

    b1, b2 = st.columns(2)
    with b1:
        st.button(
            "Usar la fábula de ejemplo",
            on_click=usar_fabula,
            use_container_width=True,
        )
    with b2:
        convertir = st.button(
            "Convertir a audio", type="primary", use_container_width=True
        )

if convertir:
    if not texto.strip():
        st.warning("Escribe o pega un texto antes de convertirlo.")
    else:
        with st.spinner("Generando audio..."):
            try:
                st.session_state["audio"] = generar_audio(
                    texto, IDIOMAS[idioma_nombre], lento
                )
            except Exception as error:
                st.error(
                    "No se pudo generar el audio. Revisa tu conexión e inténtalo "
                    f"de nuevo. ({error})"
                )

if "audio" in st.session_state:
    st.write("")
    with st.container(border=True):
        st.subheader("Tu audio")
        components.html(reproductor(st.session_state["audio"]), height=120)
        st.download_button(
            "Descargar MP3",
            data=st.session_state["audio"],
            file_name="audio.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )

st.write("")
st.caption("Voz generada con Google Text-to-Speech (gTTS).")
