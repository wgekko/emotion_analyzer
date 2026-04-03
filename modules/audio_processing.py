import librosa
import numpy as np

def extract_audio_features(file_path):
    y, sr = librosa.load(file_path, sr=None)

    # Features
    rms = librosa.feature.rms(y=y)[0]
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)[0]

    # Extraer el valor numérico del tempo de forma segura
    tempo_value = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

    # Promedios
    features = {
        "energy": float(np.mean(rms)),
        "tempo": tempo_value,
        "speech_rate": float(np.mean(zcr))
    }

    return features, y, sr