#!/usr/bin/env python3
"""
grabar_audio_raspberry.py
-----------------------
Script para Raspberry Pi Zero 2W que graba audio activado por voz (Voice Activity Detection).

Funcionalidad:
- Escucha continuamente el micrófono buscando sonido que supere un umbral.
- Cuando detecta sonido, comienza a grabar (incluyendo audio previo del pre-buffer).
- Mientras graba, monitorea el nivel de amplitud.
- Si detecta silencio prolongado (configurable), detiene la grabación.
- Guarda el audio grabado en un archivo WAV con timestamp.
- si ha conexiones a internet, envía el archivo a un servidor remoto usando SCP

Parámetros:
- -u / --umbral: Nivel de amplitud para detectar sonido (default: 1000)
- -o / --salida: Nombre del archivo WAV de salida (default: Audio<YYYY-MM-DD_HH-MM-SS>.wav)
- -d / --dispositivo: ID del micrófono a usar
- --listar: Muestra los micrófonos disponibles en el sistema

Instrucciones para Raspberry Pi Zero 2W:
1. Actualizar el sistema: sudo apt update && sudo apt upgrade
2. Instalar dependencias del sistema: sudo apt install python3-pyaudio portaudio19-dev python3-numpy
3. Instalar dependencias de Python: pip3 install pyaudio numpy
4. Configurar audio (opcional): Verificar con 'arecord -l' y ajustar dispositivo si es necesario
5 si el microfono no grab subir el volumen con > alsamixer

eviar script a rpi: scp grabar_audio_raspberry.py tadu@192.168.1.207:/home/tadu/splendid
"""

import wave
import sys
import argparse
import signal
import time
import collections
from datetime import datetime
import threading

try:
    import pyaudio
    import numpy as np
except ImportError:
    print("ERROR: Faltan dependencias.")
    print("En Raspberry Pi, instálalas ejecutando:")
    print("sudo apt install python3-pyaudio portaudio19-dev python3-numpy")
    print("pip3 install pyaudio numpy")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------
FORMATO        = pyaudio.paInt16
CANALES        = 1
TASA_MUESTREO  = 44100
CHUNK          = 1024*2
UMBRAL_DEFAULT = 1000   # Ajustar según el ruido de fondo en Raspberry Pi
SILENCIO_LIMIT = 10     # Segundos de silencio para detener la grabación
PRE_BUFFER_SEC = 0.5   # Segundos de audio previo a guardar
MAX_EN_SILENCIO = 2 #  segundos para suspender la grabación y guardar
# ---------------------------------------------------------------------------

semaforo_guardar = threading.Semaphore(1)

def listar_dispositivos(audio: pyaudio.PyAudio) -> None:
    """Muestra los dispositivos de audio disponibles en Raspberry Pi."""
    print("\n--- Dispositivos de Audio Detectados ---")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"ID [{i}]: {info['name']} (Canales de entrada: {info['maxInputChannels']})")
    print("----------------------------------------\n")

# Función para guardar el audio grabado en un archivo WAV
def guardar(frames: list, nombre_archivo: str, audio: pyaudio.PyAudio) -> None:

    global semaforo_guardar

    semaforo_guardar.acquire()  
    
    with wave.open(nombre_archivo, "wb") as wf:
        wf.setnchannels(CANALES)
        wf.setsampwidth(audio.get_sample_size(FORMATO))
        wf.setframerate(TASA_MUESTREO)
        wf.writeframes(b"".join(frames))
    semaforo_guardar.release()

    print(f"\nArchivo guardado exitosamente: {nombre_archivo}") 


def grabar_activado_por_voz(
    umbral: int,
    fichero_salida: str,
    indice_dispositivo: int | None = None
) -> None:
    
    global semaforo_guardar
    guardado = False

    # string con la fecha y hora actual para nombrar el archivo de salida
    fichero_salida = f"{datetime.now().strftime('%Y-%m-%d %H_%M_%S')}.wav"

    audio = pyaudio.PyAudio()
    
    # En Raspberry Pi, el dispositivo por defecto puede variar
    # Si no se especifica, usa el predeterminado del sistema
    try:
        stream = audio.open(
            format=FORMATO,
            channels=CANALES,
            rate=TASA_MUESTREO,
            input=True,
            input_device_index=indice_dispositivo,
            frames_per_buffer=CHUNK,
        )
    except Exception as e:
        print(f"\n[ERROR] No se pudo abrir el micrófono: {e}")
        print("Sugerencia: Ejecuta 'python3 grabar_audio_raspberry.py --listar' para ver los IDs.")
        audio.terminate()
        return

    print(f"Escuchando... (Umbral actual: {umbral})")
    print("Presiona Ctrl+C para detener y salir.")

    grabando = False
    frames_grabados = []
    
    # Buffer circular para no perder el inicio del sonido
    max_pre_frames = int(TASA_MUESTREO / CHUNK * PRE_BUFFER_SEC)
    pre_buffer = collections.deque(maxlen=max_pre_frames)
    
    silencio_inicio = None
    corriendo = True

    # Manejo de interrupción en Windows (Ctrl+C)
    def signal_handler(sig, frame):
        print("\n[!] Interrupción detectada. Deteniendo grabación...")
        nonlocal corriendo
        corriendo = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while corriendo:

            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitud_max = np.abs(audio_data).max()

                if not grabando:
                    pre_buffer.append(data)
                    if amplitud_max > umbral:
                        print(f"\n[!] ¡Sonido detectado! (Nivel: {amplitud_max}). Grabando...")
                        grabando = True
                        guardado = False
                        frames_grabados += list(pre_buffer)
                        silencio_inicio = None
                else:
                    # Seccion crítica: mientras grabo a disco
                    #----------------------------------------
                    semaforo_guardar.acquire()
                    frames_grabados.append(data)
                    semaforo_guardar.release()
                    #--------------------------------------
                    if amplitud_max > umbral:
                        silencio_inicio = None # Resetear tiempo de silencio
                    else:
                        # estoy en silencio
                      
                        try:
                            tiempoEnSilencio = time.time() - silencio_inicio
                        except TypeError:
                            tiempoEnSilencio = 0

                        print(f" > Silencio... Tiempo en silencio: {tiempoEnSilencio:.1f}s", end="\r")    
                        
                        if silencio_inicio is None:
                            silencio_inicio = time.time()
                     
                        if tiempoEnSilencio > MAX_EN_SILENCIO:
                            
                            print(f"\n[*] Silencio prolongado no incluir")
                            grabando = False

                            if not guardado:
                                hilo_guardar = threading.Thread(
                                    target=guardar,
                                    args=(frames_grabados, fichero_salida, audio),
                                    daemon=True
                                )
                                hilo_guardar.start()
                                # hasta que no grabe mas frames no dejo guardar otra vez
                                guardado = True
                            
                    print(f" > Grabando... Nivel actual: {amplitud_max:5d}", end="\r")
            except IOError:
                # Evitar que errores menores de buffer detengan el script
                continue
        print("\nDeteniendo grabación...")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    if frames_grabados: guardar(frames_grabados, fichero_salida, audio)
        
    '''
        # Asegurar que el nombre termine en .wav
        if not fichero_salida.lower().endswith(".wav"):
            fichero_salida += ".wav"
            
        with wave.open(fichero_salida, "wb") as wf:
            wf.setnchannels(CANALES)
            wf.setsampwidth(audio.get_sample_size(FORMATO))
            wf.setframerate(TASA_MUESTREO)
            wf.writeframes(b"".join(frames_grabados))
        print(f"\nArchivo guardado exitosamente: {fichero_salida}")
    else:
        print("\nNo se detectó suficiente sonido para generar una grabación.")'''

def main():
    parser = argparse.ArgumentParser(description="Grabación por umbral para Raspberry Pi Zero 2W.")
    parser.add_argument("-u", "--umbral", type=int, default=UMBRAL_DEFAULT, help="Umbral de activación (ej. 500)")
    parser.add_argument("-o", "--salida", type=str, help="Nombre del archivo WAV")
    parser.add_argument("-d", "--dispositivo", type=int, help="ID del dispositivo de entrada")
    parser.add_argument("--listar", action="store_true", help="Listar micrófonos disponibles")
    args = parser.parse_args()

    if args.listar:
        listar_dispositivos(pyaudio.PyAudio())
        return

    # Generar nombre por defecto con fecha y hora
    fichero = args.salida or f"TEST{datetime.now().strftime('%H%M%S')}.wav"
    
    grabar_activado_por_voz(args.umbral, fichero, args.dispositivo)

if __name__ == "__main__":
    main()
