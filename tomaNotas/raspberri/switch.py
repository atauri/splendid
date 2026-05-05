from gpiozero import Button
from signal import pause, SIGINT
import time
import os
import threading

button = Button(17, pull_up=True, bounce_time=0.05)

press_time = 0
LONG_PRESS_TIME = 2  # segundos

estado = None


# recupera el pid del proceso de grabación para enviar señal de interrupción desde el switch
def leerPid():
    if os.path.exists("proceso.pid"):
        with open("proceso.pid", "r") as f:
            return int(f.read().strip())        
    return None

def matarProcesoGrabacion():
    os.system("clear")
    pid = leerPid()
    if pid:
        print(f"Enviando señal de interrupción al proceso de grabación (PID: {pid})...")
        os.kill(pid, SIGINT)  # enviar señal de interrupción para detener la grabación
    else:
        print("No se encontró el PID del proceso de grabación.")

def on():

    global estado, press_time
    #print("ON")
    
    press_time = time.time()
    
    if estado == "Grabando":
            estado = None

    if estado == None:
        estado = "Grabando"
        #print("Estado: Grabar")
        os.system("python3 grabar_audio_raspberry.py &")  # iniciar grabación en segundo plano

def off():

    def check():

        # leer estado del pin 17 para verificar si el botón sigue presionado
        # si despues de 5 sg sigue en off apago
        time.sleep(5)
        if not button.is_pressed:
            os.system("python3 enviar.py")
            print("Apagar")
            #os.system("sudo shutdown -h now")        
        return

    matarProcesoGrabacion()
    # si la duracione es larga se apaga el sistema, si es corta no hace nada
    threading.Thread(target=check).start()
    

button.when_pressed = on
button.when_released = off

pause()