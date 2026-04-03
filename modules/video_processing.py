import cv2
import os

# Intentamos importar el motor optimizado en Rust
try:
    from rust_engine import extract_frames_rust
    USE_RUST = True
except ImportError:
    USE_RUST = False
    print("⚠️ Advertencia: No se encontró rust_engine. Usando cv2 de Python (más lento).")

def extract_frames(video_path, output_dir="data/temp/frames", interval=30):
    os.makedirs(output_dir, exist_ok=True)

    if USE_RUST:
        # El motor en Rust maneja el bucle a la velocidad de C/C++
        return extract_frames_rust(video_path, output_dir, interval)
    
    # Plan B: Fallback a Python puro
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_frames.append(frame_path)

        frame_count += 1

    cap.release()
    return saved_frames