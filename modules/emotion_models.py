from deepface import DeepFace
import logging

# Desactivar logs innecesarios de TensorFlow para limpiar la consola en Windows
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

def analyze_face_emotion(image_path):
    """
    Analiza la emoción de una imagen usando un detector más veloz (SSD).
    """
    try:
        # Usamos detector_backend='ssd' para un balance ideal entre velocidad y precisión
        # enforce_detection=False evita que el script explote si no hay nadie en el frame
        results = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            detector_backend='ssd', 
            enforce_detection=False,
            silent=True
        )
        
        # DeepFace devuelve una lista; tomamos el primer rostro detectado
        return results[0]["emotion"] if results else None
    except Exception as e:
        logging.error(f"Error analizando {image_path}: {e}")
        return None

def aggregate_emotions(emotion_list):
    """
    Calcula el promedio de las emociones detectadas en una serie de frames.
    """
    # Filtrar resultados Nulos
    valid_emotions = [e for e in emotion_list if e is not None]
    
    if not valid_emotions:
        return {}

    aggregated = {}
    for emotions in valid_emotions:
        for k, v in emotions.items():
            aggregated[k] = aggregated.get(k, 0) + v

    total = len(valid_emotions)
    return {k: round(v / total, 2) for k, v in aggregated.items()}