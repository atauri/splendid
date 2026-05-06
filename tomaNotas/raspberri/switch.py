from gpiozero import Button
from signal import pause, SIGINT
import time
import os
import threading

# import GIPO para controlar el zumbador
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

button = Button(17, pull_up=True, bounce_time=0.05)
 
# configurar pin 4 como salida para el zumbador
GPIO.setup(4, GPIO.OUT) 
#Button(4, pull_up=True)  # pin para el zumbador       

press_time = 0
LONG_PRESS_TIME = 2  # segundos

estado = None

def beep(beeps=1, durationH=0.1, durationL=0.1):
    print(f"Beep: {beeps} veces, duración alta: {durationH}s, duración baja: {durationL}s") 
    for _ in range(beeps):
        GPIO.output(4, GPIO.HIGH)
        time.sleep(durationH)
        GPIO.output(4, GPIO.LOW)
        time.sleep(durationL)

# recupera el pid del proceso de grabación para enviar señal de interrupción desde el switch
def leerPid():
    if os.path.exists("/home/tadu/splendid/proceso.pid"):
        with open("/home/tadu/splendid/proceso.pid", "r") as f:
            return int(f.read().strip())        
    return None

def matarProcesoGrabacion():
    os.system("clear")
    pid = leerPid()
    if pid:
        print(f"Enviando señal de interrupción al proceso de grabación (PID: {pid})...")
        try: os.kill(pid, SIGINT)  # enviar señal de interrupción para detener la grabación
        except ProcessLookupError:
            print("El proceso de grabación no se encontró.")
    else:
        print("No se encontró el PID del proceso de grabación.")

def on():

    global estado, press_time
    #print("ON")

    beep(1,0.2)

    press_time = time.time()
    
    if estado == "Grabando":
            estado = None

    if estado == None:
        estado = "Grabando"
        #print("Estado: Grabar")
        os.system("/home/tadu/env/bin/python3 /home/tadu/splendid/grabar_audio_raspberry2.py &")  # iniciar grabación en segundo plano

def off():

    beep(2,0.1)
    def check():

        # leer estado del pin 17 para verificar si el botón sigue presionado
        # si despues de 5 sg sigue en off apago
        time.sleep(5)
        if not button.is_pressed:
            os.system("/home/tadu/env/bin/python3 /home/tadu/splendid/enviar.py &")
            print("Apagar")
            beep(3,0.3)
            #os.system("sudo shutdown -h now")        
        return

    matarProcesoGrabacion()
    # si la duracione es larga se apaga el sistema, si es corta no hace nada
    # threading.Thread(target=check).start()
    


button.when_pressed = on
button.when_released = off

pause()