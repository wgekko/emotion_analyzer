def analyze_emotion(features):
    energy = features["energy"]
    tempo = features["tempo"]
    speech_rate = features["speech_rate"]

    # Reglas simples (MVP)
    if energy > 0.05 and tempo > 120:
        emotion = "Alta energía / entusiasmo"
    elif energy < 0.02:
        emotion = "Baja energía / calma"
    elif speech_rate > 0.1:
        emotion = "Nerviosismo"
    else:
        emotion = "Neutral"

    return emotion


def generate_insights(features):
    insights = []

    if features["energy"] > 0.05:
        insights.append("El audio muestra alta energía.")
    else:
        insights.append("El audio es relativamente calmado.")

    if features["tempo"] > 120:
        insights.append("Ritmo rápido, posible entusiasmo.")
    
    if features["speech_rate"] > 0.1:
        insights.append("Velocidad de habla elevada, posible nerviosismo.")

    return insights