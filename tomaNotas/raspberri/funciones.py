import urllib.request
import urllib.error
import subprocess
import time
import configuracion


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
# import GIPO para controlar el zumbador
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
# configurar pin 4 como salida para el zumbador
GPIO.setup(4, GPIO.OUT) 
#Button(4, pull_up=True)  # pin para el zumbador       


def beep(beeps=1, durationH=0.1, durationL=0.1):
    print(f"Beep: {beeps} veces, duración alta: {durationH}s, duración baja: {durationL}s") 
    for _ in range(beeps):
        GPIO.output(4, GPIO.HIGH)
        time.sleep(durationH)
        GPIO.output(4, GPIO.LOW)
        time.sleep(durationL)


def esta_conectado_a_internet() -> bool:
    """
    Verifica si hay conexión a internet intentando acceder a google.com.
    
    Retorna:
        bool: True si hay conexión, False si no.
    """
    try:
        urllib.request.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib.error.URLError:
        return False

# fucnion que mueve un fichero a la carpeta procesados
def mover_a_procesados(nombre_archivo: str) -> None:
    """
    Mueve un archivo a la carpeta 'procesados' dentro del directorio actual.
    
    Args:
        nombre_archivo: Nombre del archivo a mover (ej: "transcripcion.wav")
    """
    import shutil
    import os

    if not os.path.exists(configuracion.PATH_PROCESADOS):
        os.makedirs(configuracion.PATH_PROCESADOS)

    ruta_origen = os.path.join(configuracion.PATH_AUDIOS, nombre_archivo)
    ruta_destino = os.path.join(os.getcwd(), configuracion.PATH_PROCESADOS, nombre_archivo)
    print(f"Moviendo '{nombre_archivo}' a '{configuracion.PATH_PROCESADOS}/'...")
    try:
        shutil.move(ruta_origen, ruta_destino)
        print(f"Archivo '{nombre_archivo}' movido a '{configuracion.PATH_PROCESADOS}/'")
    except Exception as e:
        print(f"Error al mover el archivo: {e}")


# función que envía un fichero a un servidor remoto usando scp
def enviar_a_servidor_remoto(
    nombre_archivo: str,
    servidor: str = "titi.etsii.urjc.es",
    usuario: str = "tadu",
    destino: str = "/var/www/html/splendid/revisiones/wav/",
    puerto: int = 222
) -> bool:
    """
    Envía un archivo a un servidor remoto usando SCP.

    Args:
        nombre_archivo: Nombre del archivo a enviar.
        servidor: Dirección del servidor.
        usuario: Usuario en el servidor.
        destino: Ruta de destino en el servidor.
        puerto: Puerto SSH (por defecto 222).
    """
    # Ejemplo de uso: scp -P 222 "2026-05-03 11_23_14.wav" tadu@titi.etsii.urjc.es:/home/tadu/proyectos/splendid/revisiones/Zarzalejo/

    comando = f"scp -P {puerto} \"{nombre_archivo}\" {usuario}@{servidor}:\"{destino}\""
    print(comando)
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"Archivo '{nombre_archivo}' enviado a '{servidor}:{destino}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al enviar el archivo: {e}")
        return False
