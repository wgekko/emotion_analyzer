import streamlit as st
import pandas as pd
import plotly.express as px
import concurrent.futures
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import uuid
from modules.video_processing import extract_frames 
from modules.audio_processing import extract_audio_features
from modules.emotion_models import analyze_face_emotion, aggregate_emotions
from modules.fusion import calculate_score
from modules.utils import save_uploaded_file, clear_temp_data
from moviepy import VideoFileClip

# Configuración de página ancha para mejores gráficos
st.set_page_config(page_title="BioEmotion AI", page_icon=":material/comedy_mask:" ,layout="wide")

#-----------------------------------------------------------------------------

text = "Listo para analizar emociones en video!!!"
base_duration = 1

words = text.split(" ")

html = '<div class="text">'

for word_index, word in enumerate(words):
    html += f'<span class="word" style="animation-delay:{word_index * base_duration}s; animation-duration:{base_duration * len(words)}s;">'
    
    for letter_index, letter in enumerate(word):
        html += f'<span class="letter" style="animation-delay:{word_index * base_duration}s; animation-duration:{letter_index * base_duration + word_index}s;">{letter}</span>'
    
    html += '</span>&nbsp;'

html += '</div>'

st.markdown(f"""
<style>
:root {{
  --crouch-ratio: 0.9; 
  --jump-height: -180%;
  --easing: ease-in-out;
  --spin-angle: 180deg;
  --font-size: 3rem;
  --color-text: #fa2;
  --color-highlight: #4ad4;
  --color-bg: #111;
  --chaos-percentage: 0%;
}}

body {{
  background-color: var(--color-bg);
}}

.text {{
  text-align: center;
  font-size: var(--font-size);
  color: var(--color-text);
}}

.word, .letter {{
  display: inline-block;
  animation: jump var(--easing) infinite;
  transform-origin: center bottom;
}}

@keyframes jump {{
  0%, 20% {{
    transform: scaleY(1);
  }}
  25% {{
    transform: scaleY(var(--crouch-ratio));
  }}
  30% {{
    transform: scaleY(var(--crouch-ratio)) translateY(var(--jump-height)) rotateX(var(--spin-angle));
    background-color: var(--color-highlight);
    padding: 0 var(--chaos-percentage);
  }}
  40% {{
    transform: translateY(0) scaleY(1) rotateX(0deg);
  }}
  45% {{
    transform: scaleY(var(--crouch-ratio));
  }}
  100% {{
    transform: scaleY(1);
  }}
}}
</style>

{html}
""", unsafe_allow_html=True)

#-----------------------------------------------------------------------------

st.header(":material/video_file: Analizador Emocional Multimodal (video)")
st.markdown("---")

# --- LÓGICA DE PROCESAMIENTO ---

def process_video_pipeline(video_path):
    """Extrae frames y analiza la evolución emocional segundo a segundo."""
    # Intervalo de 30 frames (aprox 1 segundo en videos estándar)
    interval = 30 
    frames = extract_frames(video_path, interval=interval)
    
    timeline_results = []
    
    # Procesamos los frames obtenidos
    for i, frame_path in enumerate(frames):
        emotion_data = analyze_face_emotion(frame_path)
        if emotion_data:
            # Estructura para el gráfico de línea de tiempo
            entry = {"segundo": i}
            entry.update(emotion_data)
            timeline_results.append(entry)
            
    return timeline_results

def process_audio_pipeline(video_path):
    """Extrae y analiza el audio en un hilo separado."""
    unique_id = uuid.uuid4().hex
    audio_path = f"data/temp/audio_{unique_id}.wav"
    
    try:
        with VideoFileClip(video_path) as clip:
            clip.audio.write_audiofile(audio_path, logger=None)
        
        audio_features, _, _ = extract_audio_features(audio_path)
        return audio_features
    finally:
        # Limpieza inmediata del audio temporal para evitar bloqueos en Windows
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass

# --- INTERFAZ DE USUARIO ---

uploaded_file = st.file_uploader("Sube un video para analizar (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file:
    # 1. Limpieza preventiva de sesiones anteriores
    clear_temp_data()
    
    # 2. Guardar y mostrar video
    video_path = save_uploaded_file(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.video(uploaded_file)
    
    with col2:
        st.info("⚡ Procesando con motor optimizado (Rust + SSD Detector)...")
        status_placeholder = st.empty()
        
        with st.spinner("Analizando biometría..."):
            # 3. EJECUCIÓN EN PARALELO (Multithreading)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_video = executor.submit(process_video_pipeline, video_path)
                future_audio = executor.submit(process_audio_pipeline, video_path)

                timeline_data = future_video.result()
                audio_features = future_audio.result()

        st.success(":material/assignment_turned_in: Análisis completado")

    st.markdown("---")

    # --- VISUALIZACIÓN DE RESULTADOS ---

    if timeline_data:
        # Crear DataFrame para la línea de tiempo
        df_timeline = pd.DataFrame(timeline_data)
        
        # Fila 1: Línea de Tiempo
        st.subheader(":material/avg_time: :material/mood: Evolución Emocional en el Tiempo")
        df_melted = df_timeline.melt(id_vars=["segundo"], var_name="Emoción", value_name="Intensidad")
        fig_line = px.line(df_melted, x="segundo", y="Intensidad", color="Emoción", 
                        markers=True, template="plotly_dark")
        st.plotly_chart(fig_line, width='stretch' ) #width='stretch'

        # Fila 2: Resumen y Score
        col_a, col_b = st.columns(2)
        st.write("---")
        with col_a:
            st.subheader(":material/android_cell_5_bar_plus: Promedio de Intensidad")
            # Promediar todas las columnas excepto 'segundo'
            avg_emotions = df_timeline.drop(columns=["segundo"]).mean().to_dict()
            df_avg = pd.DataFrame(list(avg_emotions.items()), columns=["Emoción", "Valor"])
            fig_bar = px.bar(df_avg, x="Emoción", y="Valor", color="Emoción", template="plotly_dark")
            st.plotly_chart(fig_bar,  width='stretch' ) #width='stretch'
            
        with col_b:
            st.subheader(":material/analytics: Métricas de Engagement")
            # Calculamos el score final usando la lógica de fusión
            final_score = calculate_score(avg_emotions, audio_features)
            st.metric(label="Score de Impacto Emocional", value=f"{final_score}/100")
            st.write("---")
            st.write("**Insights de Audio:**")
            st.json(audio_features)

    else:
        st.error("No se detectaron rostros suficientes para generar un análisis detallado.")

st.sidebar.title(":material/settings_alert: Configuración")
st.sidebar.write("Motor: **Optimizado (Rust Engine)**")
st.sidebar.write("Detector: **SSD (Fast Inerence)**")
if st.sidebar.button("Limpiar Caché Manualmente"):
    clear_temp_data()
    st.sidebar.success("Carpeta data/temp vaciada.")