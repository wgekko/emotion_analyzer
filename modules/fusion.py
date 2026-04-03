def calculate_score(emotions, audio_features):
    score = 0

    # Usamos .get() que devuelve 0 si la clave no existe, evitando errores
    score += emotions.get("happy", 0)

    score += audio_features.get("energy", 0) * 100

    return round(score / 2, 2)