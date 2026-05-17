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


from colorama import  Fore
import os
import wave
import sys
import argparse
import signal
import time
import collections
from datetime import datetime
import threading

import configuracion
import RPi.GPIO as GPIO


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
UMBRAL_DEFAULT = 200   # Ajustar según el ruido de fondo en Raspberry Pi
SILENCIO_LIMIT = 10     # Segundos de silencio para Guardar en disco
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

# Función para guardar SOLO los nuevos chunks en un archivo WAV
def guardar(frames: list, archivo_wav) -> None:
    

    global semaforo_guardar

    semaforo_guardar.acquire()  
    try:
        # Escribir solo los nuevos frames
        archivo_wav.writeframes(b"".join(frames))
        frames.clear()  # Limpiar la lista de frames después de guardar
    finally:
        semaforo_guardar.release()

    #os.system("clear")
    print(f"\n{len(frames)} frames guardados ") 


def grabar_activado_por_voz(
    umbral: int,
    fichero_salida: str,
    indice_dispositivo: int | None = None
) -> None:
    
    global semaforo_guardar
    guardado = False

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)
    
    
    # Encender LED al iniciar el script
    # contar numero ficheros wav en el directorio
    num_wav = len([f for f in os.listdir(configuracion.PATH_AUDIOS) if f.endswith(".wav")])
    fichero_salida = f"grabacion_{num_wav + 1}.wav"

    # Si pilla fecha y hora sobreescribe el nombre.
    # string con la fecha y hora actual para nombrar el archivo de salida
    try: fichero_salida = f"{datetime.now().strftime('%Y-%m-%d %H_%M_%S')}.wav"
    except: pass

    # Guardar el WAV en el directorio de configuracion
    if not os.path.isabs(fichero_salida):
        fichero_salida = os.path.join(configuracion.PATH_AUDIOS, fichero_salida)

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

    archivo_wav = None  # Objeto del archivo WAV abierto

    frames_a_guardar = []  # Lista para almacenar los frames que se van a guardar en disco
    
    # Buffer circular para no perder el inicio del sonido
    max_pre_frames = int(TASA_MUESTREO / CHUNK * PRE_BUFFER_SEC)
    pre_buffer = collections.deque(maxlen=max_pre_frames)

    estado = "--"
    tiempoEnSilencio = 0
    silencio_inicio = None
    corriendo = True
        
    GPIO.output(23, GPIO.LOW)  # Apagar LED al iniciar la escucha activa
    
    # Manejo de interrupción en Windows (Ctrl+C)
    def signal_handler(sig, frame):
        print("\n[!] Interrupción detectada. Deteniendo grabación...")
        nonlocal corriendo
        corriendo = False  # salir del bucle principal para cerrar el stream y guardar el archivo
        time.sleep(1)  # Dar tiempo a que el proceso termine
        
    # ESCUCHAR LA SEÑAL DE INTERRUPCIÓN PARA DETENER LA GRABACIÓN    
    signal.signal(signal.SIGINT, signal_handler)
                        

    try:
        os.system("clear")

        estado_anterior = None
        while corriendo:

            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                amplitud_max = np.abs(audio_data).max()
                media = int(np.abs(audio_data).mean())
                
                # mostrar información de nivel de audio y estado actual
                estado_anterior = estado
                if media > umbral:
                    
                    estado = "G"
                    GPIO.output(23, GPIO.HIGH)  # Encender LED al detectar sonido
                    guardado = False  # Reiniciar bandera de guardado al detectar sonido
                    silencio_inicio = time.time()  # resetear tiempo de silencio al detectar sonido
                    if archivo_wav is None:
                        # Abrir el archivo WAV al detectar sonido por primera vez
                        archivo_wav = wave.open(fichero_salida, "wb")
                        archivo_wav.setnchannels(CANALES)
                        archivo_wav.setsampwidth(audio.get_sample_size(FORMATO))
                        archivo_wav.setframerate(TASA_MUESTREO)
                else:
                    GPIO.output(23, GPIO.LOW)  # Apagar LED al no detectar sonido
                    if estado_anterior =='P': pass
                    else : estado = "S"
                    
                    try:
                        tiempoEnSilencio = time.time() - silencio_inicio
                    except TypeError:
                        tiempoEnSilencio = 0
                    
                    if  tiempoEnSilencio > MAX_EN_SILENCIO and  estado != 'P':
                        estado = "P" # Pausado por silencio prolongado
                        if not guardado and len(frames_a_guardar)>0:
                            hilo_guardar = threading.Thread(
                                target=guardar,
                                args=(frames_a_guardar, archivo_wav),
                                daemon=True
                            )
                            hilo_guardar.start()
                            guardado = True
                
                if estado == 'S' or estado == 'G':
                    pre_buffer.append(data)
                    frames_a_guardar += list(pre_buffer)
                    pre_buffer.clear()  # Limpiar el pre-buffer después de agregar sus frames a la lista de guardado
                else:
                    pass
                
                # mostrar valores si cambia el estado 
                if estado != estado_anterior:
                    print(f"Estado: {estado}, Media: {media:5d}, Max: {amplitud_max:5d}, umbral: {umbral}, silencio: {tiempoEnSilencio:.1f}", end="\r")
  
            except IOError:
                # Evitar que errores menores de buffer detengan el script
                continue
        print("\nFIN")

    finally:
        GPIO.output(23, GPIO.HIGH)
        guardar(frames_a_guardar, archivo_wav)  # Guardar cualquier frame restante antes de cerrar
        stream.stop_stream()
        stream.close()
        audio.terminate()
        # Cerrar el archivo WAV si está abierto
        if archivo_wav:
            archivo_wav.close()
            print(f"Archivo guardado exitosamente: {fichero_salida}")
           


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
    fichero = args.salida or f"{datetime.now().strftime('%H%M%S')}.wav"
    grabar_activado_por_voz(args.umbral, fichero, args.dispositivo)

if __name__ == "__main__":
    main()
