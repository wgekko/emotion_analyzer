import os
import shutil
import yt_dlp

def save_uploaded_file(uploaded_file, path="data/temp"):
    """Guarda un archivo subido localmente."""
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# def download_web_video(url, path="data/temp"):
#     """Descarga video/audio de la web usando yt-dlp."""
#     os.makedirs(path, exist_ok=True)
    
#     # Plantilla del nombre de archivo: web_download.mp4
#     output_template = os.path.join(path, "web_download.%(ext)s")
    
#     ydl_opts = {
#         # Forzamos MP4 para compatibilidad con OpenCV y MoviePy
#         'format': 'bestvideo[ext=mp4]+bestaudio[m4a]/best[ext=mp4]/best',
#         'outtmpl': output_template,
#         'quiet': True,
#         'noplaylist': True,
#         'overwrites': True,
#     }
    
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
#         return ydl.prepare_filename(info)

def download_web_video(url, path="data/temp"):
    """Descarga video/audio de la web usando yt-dlp de forma robusta."""
    os.makedirs(path, exist_ok=True)
    
    # Usamos una plantilla simple para evitar conflictos de extensión
    output_template = os.path.join(path, "web_download.%(ext)s")
    
    ydl_opts = {        
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4/best',
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True,
        'overwrites': True,
        # Esto ayuda a evitar errores de certificado en algunos Linux
        'nocheckcertificate': True, 
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def clear_temp_data(temp_dir="data/temp"):
    """Limpia la caché temporal."""
    if not os.path.exists(temp_dir): return
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error limpiando: {e}")



# import os
# import shutil
# import yt_dlp

# def save_uploaded_file(uploaded_file, path="data/temp"):
#     os.makedirs(path, exist_ok=True)
#     file_path = os.path.join(path, uploaded_file.name)

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     return file_path

# def download_web_video(url, path="data/temp"):
#     """Descarga video/audio de YouTube u otras webs usando yt-dlp."""
#     os.makedirs(path, exist_ok=True)
#     output_template = os.path.join(path, "web_download.%(ext)s")
    
#     ydl_opts = {
#         'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
#         'outtmpl': output_template,
#         'quiet': True,
#         'noplaylist': True,
#     }
    
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
#         return ydl.prepare_filename(info)


# def clear_temp_data(temp_dir="data/temp"):
#     """
#     Limpia todos los archivos dentro de la carpeta temporal para evitar 
#     acumulación de frames y audios.
#     """
#     if not os.path.exists(temp_dir):
#         return

#     for filename in os.listdir(temp_dir):
#         file_path = os.path.join(temp_dir, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path) # Borra archivo o link
#             elif os.path.isdir(file_path):
#                 shutil.rmtree(file_path) # Borra carpetas (como /frames)
#         except Exception as e:
#             print(f"No se pudo borrar {file_path}. Motivo: {e}")