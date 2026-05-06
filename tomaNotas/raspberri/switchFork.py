from gpiozero import Button
from signal import pause, SIGINT
import os

import funciones



button = Button(17, pull_up=True, bounce_time=0.05)
        
pidPadre = os.getpid()
pidHijo = None
estado = None

print(f"PID del proceso principal: {pidPadre}") 

# recupera el pid del proceso de grabación para enviar señal de interrupción desde el switch

def matarProcesoGrabacion():

    if pidHijo is not None:
        print(f"Enviando señal de interrupción al proceso de grabación (PID: {pidHijo})...")
        try: os.kill(pidHijo, SIGINT)  # enviar señal de interrupción para detener la grabación
        except ProcessLookupError:
            print("El proceso de grabación no se encontró.")
    else:
        print("No se encontró el PID del proceso de grabación.")

def on():

    global estado
    funciones.beep(1,0.2)

    # Crear un proceso hijo para ejecutar la grabación en segundo plano  
    
    os.fork()

    # el hijo carga con exec el script de grabación, el padre continúa con el programa principal

    if os.getpid() != pidPadre and estado != "Grabando": 
        print(f"PID del proceso hijo: {os.getpid()}")    # Solo el proceso hijo ejecutará la grabación
        os.execv("/home/tadu/env/bin/python3", ["/home/tadu/env/bin/python3", "/home/tadu/splendid/grabar_audio_raspberryFork.py"])    
    else:
        # soy el padre
        estado = "Grabando"
        
def off():

    global estado 
    estado = None
    print("OFF")
    funciones.beep(2,0.1)
    matarProcesoGrabacion()
    

button.when_pressed = on
button.when_released = off

# Ready
funciones.beep(1,1)

pause()