import os
# Silenciar mensajes de TensorFlow al inicio
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import concurrent.futures
import uuid
# Importamos también AudioFileClip para soportar archivos 100% audio
from moviepy import VideoFileClip, AudioFileClip

# Importaciones de tus módulos
from modules.video_processing import extract_frames 
from modules.audio_processing import extract_audio_features
from modules.emotion_models import analyze_face_emotion, aggregate_emotions
from modules.fusion import calculate_score
from modules.utils import save_uploaded_file, clear_temp_data, download_web_video

# Configuración de página
st.set_page_config(page_title="BioEmotion AI", page_icon=":material/comedy_mask:" ,layout="wide")

#-----------------------------------------------------------------------------
# Animación de dashboard

text = "Vamos a analizar emociones en video/audio !!!"
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
st.markdown("---")

st.header(":material/video_file: Analizador Emocional Multimodal (video/audio)")
st.markdown("---")

# --- LÓGICA DE PROCESAMIENTO ---

def process_video_pipeline(video_path):
    """Extrae frames y analiza la evolución emocional."""
    interval = 30 
    frames = extract_frames(video_path, interval=interval)
    
    timeline_results = []
    for i, frame_path in enumerate(frames):
        emotion_data = analyze_face_emotion(frame_path)
        if emotion_data:
            entry = {"segundo": i}
            entry.update(emotion_data)
            timeline_results.append(entry)
            
    return timeline_results

def process_audio_pipeline(video_path, is_only_audio=False):
    """Extrae y analiza el audio, soportando tanto video como audio puro."""
    unique_id = uuid.uuid4().hex
    audio_path = f"data/temp/audio_{unique_id}.wav"
    
    try:
        if is_only_audio:
            with AudioFileClip(video_path) as clip:
                clip.write_audiofile(audio_path, logger=None)
        else:
            with VideoFileClip(video_path) as clip:
                if clip.audio is not None:
                    clip.audio.write_audiofile(audio_path, logger=None)
                else:
                    return {} # Si el video no tiene pista de audio
        
        audio_features, _, _ = extract_audio_features(audio_path)
        return audio_features
    except Exception as e:
        st.error(f"Error procesando audio: {e}")
        return {"energy": 0, "tempo": 0, "speech_rate": 0}
    finally:
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass

# --- INTERFAZ DE USUARIO ---

st.sidebar.title(":material/settings_alert: Configuración")
source_option = st.sidebar.radio("Fuente de entrada:", ["Archivo Local", "Enlace Web (URL)"])

video_path = None

if source_option == "Archivo Local":
    uploaded_file = st.file_uploader("Sube video o audio", type=["mp4", "mov", "avi", "wav", "mp3"])
    if uploaded_file:
        clear_temp_data()
        video_path = save_uploaded_file(uploaded_file)
else:
    url_input = st.text_input("Pega el enlace (YouTube, etc.):", placeholder="https://www.youtube.com/watch?v=...")
    st.info("Luego de cargar el link presionar enter. Importante: YouTube puede bloquear la dirección del link.")
    if url_input:
        if st.button("Descargar y Analizar"):
            clear_temp_data()
            with st.spinner("Descargando contenido..."):
                try:
                    video_path = download_web_video(url_input)
                    st.success(":material/done_all:  Descarga completa")
                except Exception as e:
                    st.error(f"Error de descarga: {e}")

# --- EJECUCIÓN DEL ANÁLISIS ---

if video_path:
    is_only_audio = video_path.lower().endswith(('.mp3', '.wav'))
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if is_only_audio:
            st.audio(video_path)
        else:
            st.video(video_path)
    
    with col2:
        st.info("⚡ Procesando con motor optimizado (Rust + SSD Detector)...")
        status_placeholder = st.empty()
        
        with st.spinner("Procesando biometría..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Si es solo audio, no ejecutamos el pipeline de video
                future_video = executor.submit(process_video_pipeline, video_path) if not is_only_audio else None
                future_audio = executor.submit(process_audio_pipeline, video_path, is_only_audio)

                timeline_data = future_video.result() if future_video else []
                audio_features = future_audio.result()

        st.success(":material/done_all: Análisis completado")

    st.markdown("---")

    # --- VISUALIZACIÓN DE VIDEO ---

    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        st.subheader(":material/avg_time: :material/mood: Evolución Emocional Visual")
        df_melted = df_timeline.melt(id_vars=["segundo"], var_name="Emoción", value_name="Intensidad")
        fig_line = px.line(df_melted, x="segundo", y="Intensidad", color="Emoción", markers=True, template="plotly_dark")
        st.plotly_chart(fig_line, width='stretch')

        st.markdown("---")
        st.subheader(":material/bar_chart: Resumen de Sentimientos Visuales")
        
        df_avg = pd.DataFrame(timeline_data).drop(columns=["segundo"]).mean()
        avg_emotions = df_avg.to_dict()
        
        df_bar = pd.DataFrame({"Emoción": df_avg.index, "Promedio": df_avg.values})
        fig_bar = px.bar(
            df_bar, x="Emoción", y="Promedio", color="Emoción",
            text_auto='.2f', template="plotly_dark"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, width='stretch')
    else:
        avg_emotions = {}

    # --- VISUALIZACIÓN DE AUDIO (DASHBOARD NUEVO) ---
    
    if audio_features:
        st.markdown("---")
        st.subheader(":material/graphic_eq: Dashboard Analítico de Prosodia y Voz")
        
        # Filtramos para asegurar que solo graficamos datos numéricos
        datos_numericos = {k: v for k, v in audio_features.items() if isinstance(v, (int, float))}
        
        if datos_numericos:
            col_g, col_r, col_b = st.columns(3)
            
            # 1. GAUGE CHART (Score de Impacto)
            with col_g:
                # Calculamos el score combinando lo visual (si hay) y el audio
                final_score = calculate_score(avg_emotions, audio_features)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = final_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Impacto Emocional Total", 'font': {'size': 18, 'color': 'white'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#00FFCC"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'steps': [
                            {'range': [0, 33], 'color': "#1E1E1E"},
                            {'range': [33, 66], 'color': "#2D2D2D"},
                            {'range': [66, 100], 'color': "#3C3C3C"}],
                    }
                ))
                fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_gauge, width='stretch')

            # 2. RADAR CHART (Huella Acústica)
            with col_r:
                categorias = list(datos_numericos.keys())
                valores = list(datos_numericos.values())
                
                # Cerrar el polígono
                if len(categorias) > 2:
                    categorias.append(categorias[0])
                    valores.append(valores[0])
                    
                    fig_radar = go.Figure(data=go.Scatterpolar(
                        r=valores,
                        theta=categorias,
                        fill='toself',
                        fillcolor='rgba(0, 255, 204, 0.2)',
                        line=dict(color='#00FFCC', width=2)
                    ))
                    fig_radar.update_layout(
                        title=dict(text="Perfil Acústico", font=dict(size=18, color="white")),
                        polar=dict(
                            radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.2)", tickfont=dict(color="rgba(255,255,255,0.5)")),
                            angularaxis=dict(gridcolor="rgba(255,255,255,0.2)")
                        ),
                        showlegend=False,
                        height=300, margin=dict(l=40, r=40, t=50, b=40), paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_radar, width='stretch')
                else:
                    st.info("No hay suficientes métricas para generar el radar.")

            # 3. BAR CHART HORIZONTAL (Desglose)
            with col_b:
                df_sorted = pd.DataFrame(list(datos_numericos.items()), columns=["Métrica", "Valor"]).sort_values(by="Valor", ascending=True)
                fig_bars = px.bar(
                    df_sorted, x="Valor", y="Métrica", orientation='h', color="Valor",
                    color_continuous_scale="Tealgrn", title="Desglose de Parámetros"
                )
                fig_bars.update_layout(
                    height=300, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False
                )
                fig_bars.update_xaxes(title_text="", showgrid=True, gridcolor="rgba(255,255,255,0.1)")
                fig_bars.update_yaxes(title_text="")
                st.plotly_chart(fig_bars, width='stretch')

            with st.expander("Ver JSON Completo de Métricas de Voz"):
                st.json(audio_features)

if st.sidebar.button("Limpiar todo"):
    clear_temp_data()
    st.rerun()

#-----------------------------------------------------------------
## opcion sin grafico de barra de resumen de sentimientos 

#import os
# Silenciar mensajes de TensorFlow al inicio
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import concurrent.futures
# import uuid
# from moviepy import VideoFileClip
# # Importaciones de tus módulos
# from modules.video_processing import extract_frames 
# from modules.audio_processing import extract_audio_features
# from modules.emotion_models import analyze_face_emotion, aggregate_emotions
# from modules.fusion import calculate_score
# from modules.utils import save_uploaded_file, clear_temp_data, download_web_video

# # Configuración de página
# st.set_page_config(page_title="BioEmotion AI", layout="wide")

# st.title("🎥 Analizador Emocional Multimodal")
# st.markdown("---")

# # --- LÓGICA DE PROCESAMIENTO ---

# def process_video_pipeline(video_path):
#     """Extrae frames y analiza la evolución emocional."""
#     interval = 30 
#     frames = extract_frames(video_path, interval=interval)
    
#     timeline_results = []
#     for i, frame_path in enumerate(frames):
#         emotion_data = analyze_face_emotion(frame_path)
#         if emotion_data:
#             entry = {"segundo": i}
#             entry.update(emotion_data)
#             timeline_results.append(entry)
            
#     return timeline_results

# def process_audio_pipeline(video_path):
#     """Extrae y analiza el audio."""
#     unique_id = uuid.uuid4().hex
#     audio_path = f"data/temp/audio_{unique_id}.wav"
    
#     try:
#         with VideoFileClip(video_path) as clip:
#             clip.audio.write_audiofile(audio_path, logger=None, fps=44100)
        
#         audio_features, _, _ = extract_audio_features(audio_path)
#         return audio_features
#     except Exception as e:
#         st.error(f"Error procesando audio: {e}")
#         return {"energy": 0, "tempo": 0, "speech_rate": 0}
#     finally:
#         if os.path.exists(audio_path):
#             try: os.remove(audio_path)
#             except: pass

# # --- INTERFAZ DE USUARIO ---

# st.sidebar.title("Configuración")
# source_option = st.sidebar.radio("Fuente de entrada:", ["Archivo Local", "Enlace Web (URL)"])

# video_path = None

# if source_option == "Archivo Local":
#     uploaded_file = st.file_uploader("Sube video o audio", type=["mp4", "mov", "avi", "wav", "mp3"])
#     if uploaded_file:
#         clear_temp_data()
#         video_path = save_uploaded_file(uploaded_file)
# else:
#     st.info("importante si ingresa un link de Youtube es probable que la pagina bloqueo el acceso al mismo")
#     url_input = st.text_input("Pega el enlace (YouTube, etc.):", placeholder="https://www.youtube.com/watch?v=...")
#     if url_input:
#         if st.button("Descargar y Analizar"):
#             clear_temp_data()
#             with st.spinner("Descargando contenido..."):
#                 try:
#                     video_path = download_web_video(url_input)
#                     st.success("✅ Descarga completa")
#                 except Exception as e:
#                     st.error(f"Error de descarga: {e}")

# # --- EJECUCIÓN DEL ANÁLISIS ---

# if video_path:
#     # Detectar si es solo audio por la extensión
#     is_only_audio = video_path.lower().endswith(('.mp3', '.wav'))
    
#     col1, col2 = st.columns([1, 1])
#     with col1:
#         st.video(video_path)
    
#     with col2:
#         st.info("⚡ Iniciando análisis multimodal...")
        
#         with st.spinner("Procesando biometría..."):
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 # Solo procesamos video si no es un archivo de audio puro
#                 future_video = executor.submit(process_video_pipeline, video_path) if not is_only_audio else None
#                 future_audio = executor.submit(process_audio_pipeline, video_path)

#                 timeline_data = future_video.result() if future_video else []
#                 audio_features = future_audio.result()

#         st.success("✅ Análisis completado")

#     st.markdown("---")

#     # --- VISUALIZACIÓN ---

#     if timeline_data:
#         df_timeline = pd.DataFrame(timeline_data)
#         st.subheader("📈 Evolución Emocional (Visual)")
#         df_melted = df_timeline.melt(id_vars=["segundo"], var_name="Emoción", value_name="Intensidad")
#         fig_line = px.line(df_melted, x="segundo", y="Intensidad", color="Emoción", markers=True, template="plotly_dark")
#         st.plotly_chart(fig_line, width='stretch')

#     # Métricas finales
#     col_a, col_b = st.columns(2)
#     with col_a:
#         st.subheader("📊 Métricas de Voz")
#         st.json(audio_features)
        
#     with col_b:
#         st.subheader("🎯 Engagement Final")
#         # Si no hay datos de video, usamos un diccionario vacío para la fusión
#         avg_emotions = pd.DataFrame(timeline_data).drop(columns=["segundo"]).mean().to_dict() if timeline_data else {}
#         final_score = calculate_score(avg_emotions, audio_features)
#         st.metric(label="Impacto Emocional Total", value=f"{final_score}/100")

# if st.sidebar.button("Limpiar todo"):
#     clear_temp_data()
#     st.rerun()

