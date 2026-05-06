from gpiozero import Button
from signal import pause, SIGINT
import os

import funciones



button = Button(17, pull_up=True, bounce_time=0.05)
        

# recupera el pid del proceso de grabación para enviar señal de interrupción desde el switch
def leerPid():
    if os.path.exists("/home/tadu/splendid/proceso.pid"):
        with open("/home/tadu/splendid/proceso.pid", "r") as f:
            pid = int(f.read().strip())
            print(f"PID del proceso de grabación: {pid}")       
            return
    print("No se encontró el archivo de PID.")
    return False

def matarProcesoGrabacion():

    pid = leerPid()
    if pid:
        print(f"Enviando señal de interrupción al proceso de grabación (PID: {pid})...")
        try: os.kill(pid, SIGINT)  # enviar señal de interrupción para detener la grabación
        except ProcessLookupError:
            print("El proceso de grabación no se encontró.")
    else:
        print("No se encontró el PID del proceso de grabación.")

def on():

    print("ON")
    funciones.beep(1,0.2)
    #os.system("/home/tadu/env/bin/python3 /home/tadu/splendid/grabar_audio_raspberry2.py >> /home/tadu/splendid/grabacion.log 2>&1 &")

def off():
    print("OFF")
    funciones.beep(2,0.1)
    matarProcesoGrabacion()
    

button.when_pressed = on
button.when_released = off

# Ready
funciones.beep(1,1)

pause()