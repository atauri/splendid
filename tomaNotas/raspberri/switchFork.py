from gpiozero import Button
from signal import pause, SIGINT
import os
import time

import funciones


# REC / STOP
button = Button(17, pull_up=True, bounce_time=0.05)
# Apagar / enviar
button2 = Button(15, pull_up=True, bounce_time=0.05)
        
pidPadre = os.getpid()
pidHijo = None
estado = None

print(f"PID del proceso principal: {pidPadre}") 

# recupera el pid del proceso de grabación para enviar señal de interrupción desde el switch
def matarProcesoGrabacion(p):

    print(f"Matar proceso (PID: {p})")

    print(f"Enviando señal de interrupción al proceso de grabación (PID: {p})...")
    #time.sleep(3)
    try: 
        os.kill(p , SIGINT)  # enviar señal de interrupción para detener la grabación
        return True
    except ProcessLookupError:
            print("error")
    return False


def on():

    global estado
    global pidHijo

    funciones.beep(1, 0.5)

    # Crear un proceso hijo para ejecutar la grabación en segundo plano  
    
    pidHijo = os.fork()

    # el hijo carga con exec el script de grabación, el padre continúa con el programa principal
    if os.getpid() != pidPadre:

        print(f"PID del proceso hijo: {os.getpid()}")    # Solo el proceso hijo ejecutará la grabación
        time.sleep(3)  # Esperar un poco antes de ejecutar el script de grabación
        if estado != "Grabando": 
            os.execv("/home/tadu/env/bin/python3", ["/home/tadu/env/bin/python3", "/home/tadu/splendid/grabar_audio_raspberryFork.py"])    
    else:
        # soy el padre
        estado = "Grabando"
        
def off():

    global estado 
    global pidHijo

    print("OFF")
    funciones.beep(2,0.05)

    print("Intentando matar el proceso hijo:", pidPadre, " -> pidHijo:", pidHijo)
    
    if matarProcesoGrabacion(pidHijo): estado = None

#-- switch de enviar / apagar -------------------------------------------------------------------------------------------------
    

def apagar():

    print("Apagar")
    funciones.beep(1, 1)
    os.system("sudo shutdown -h now")
        
def  enviar():

    print("Enviar")
    funciones.beep(2, 0.5)
    os.system("/home/tadu/env/bin/python3 /home/tadu/splendid/enviar.py")

   

button.when_pressed = on
button.when_released = off

button2.when_pressed = apagar
button2.when_released = enviar

# Ready
funciones.beep(1, 0.05)

pause()