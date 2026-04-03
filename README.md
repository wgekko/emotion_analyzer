# BioEmotion AI: Multimodal Emotional Intelligence Engine

**BioEmotion AI** es una plataforma de análisis bio-sensorial avanzada que combina visión artificial y procesamiento de señales acústicas para decodificar estados emocionales en tiempo real. Utilizando un motor híbrido de **Rust** y **Python**, la aplicación permite extraer métricas críticas de archivos de video, audio local o streams de YouTube.

## Características Principales

-**Análisis Multimodal:** Fusión de datos faciales (SSD Detector) y parámetros prosódicos de voz.
-**Dynamic Dashboard:** Visualización interactiva con Plotly (Radar Charts, Gauge Meters y Time-series).
-**Hybrid Core:** Procesamiento de alta eficiencia con integración de bibliotecas de sistemas.
-**Web-Ready:** Soporte nativo para descarga y análisis directo de URLs externas.

## Stack Tecnológico

-**Frontend:** Streamlit (UI Reactiva).
-**ML/Inference:** TensorFlow / OpenCV / SSD MobileNet.
-**Audio Engine:** MoviePy / Librosa (Acoustic Feature Extraction).
-**Performance:** Rust Engine (Backend de procesamiento optimizado).
-**Data:** Pandas / Plotly Express & Graph Objects.

## ⚙️ Instalación y Ejecución

### 1. Clonar el repositorio


git clone [https://github.com/wgekko/emotion_analyzer.git](https://github.com/wgekko/emotion_analyzer.git)
cd emotion_analyzer


Bash
2. Configurar el entorno (Recomendado: Conda o venv)

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Variables de Entorno
Crea un archivo .env en la raíz con la ruta de tus librerías de compilación (necesario para el motor Rust/Clang):

Fragmento de código
LIBCLANG_PATH=/usr/lib/llvm-14/lib  # Ajusta según tu sistema

4. Lanzar la App

para mantener la configuración  del la app deben crear una carpeta .streamlit y colocar el archivo lllamda config.toml que esta dentro del 
carpeta del mismo nombre 

streamlit run app.py
