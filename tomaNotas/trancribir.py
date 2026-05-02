import whisper
import os
import glob
from pathlib import Path
import funciones

modelo: str = "medium" # small no separa las oraciones
model = whisper.load_model(modelo)

def obtener_archivos_wav():
    """
    Lee todos los ficheros con extensión .wav del directorio actual.
    
    Retorna:
        list: Lista de rutas de archivos .wav encontrados
    """
    audios = glob.glob("*.wav")
    
    for i, audio in enumerate(audios):
        print(f"{i+1}. {audio} \n---------")
        txt = transcribir_audio(audio)
        guardar_transcripcion(audio, txt) 
        funciones.mover_a_procesados(audio)  

    return audios

def guardar_transcripcion(nombre_archivo_wav: str, texto: str) -> None:
    """
    Guarda el texto transcrito en un archivo .txt con el mismo nombre que el audio.
    
    Args:
        nombre_archivo_wav: Nombre del archivo WAV (ej: "grabacion.wav")
        texto: Texto a guardar
    """
    # Cambiar extensión de .wav a .txt
    ruta_txt = Path(nombre_archivo_wav).with_suffix(".txt")
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    
    print(f"Transcripción guardada en: {ruta_txt}")
    

def transcribir_audio(audio_path: str) -> str:
    """
    Transcribe un archivo de audio utilizando el modelo Whisper.
    
    Args:
        audio_path (str): Ruta al archivo de audio .wav

    Returns:
        str: Texto transcrito del audio
    """
    result = model.transcribe(audio_path, language="es", prompt="Puntúa bien las oraciones.")
    print(f"\nTranscripción de '{audio_path}':\n{result['text']}\n")
    return result["text"]    

'''

# Ruta a tu archivo WAV
audio_path = "./audio.wav"

# Transcribir (forzando español)
result = model.transcribe(audio_path, language="es")

# Mostrar texto completo
print("Transcripción:")
print(result["text"])

# Opcional: guardar en archivo
with open("transcripcion.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])'''

obtener_archivos_wav()