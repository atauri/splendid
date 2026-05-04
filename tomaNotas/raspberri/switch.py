from gpiozero import Button
from signal import pause
import time
import os
import threading

button = Button(17, pull_up=True, bounce_time=0.05)

press_time = 0
LONG_PRESS_TIME = 2  # segundos

estado = None


def on():

    global estado, press_time
    #print("ON")
    
    press_time = time.time()
    
    if estado == "Grabando":
        print("reset grabación")

    if estado == None:
        estado = "Grabando"
        print("Estado: Grabando")

    
def off():

    def check():

        # leer esdo del pin 17 para verificar si el botón sigue presionado
        time.sleep(5)
        if not button.is_pressed:
            print("Apagar")
            os.system("sudo shutdown -h now")        
        return

    # si la duracione es larga se apaga el sistema, si es corta no hace nada
    threading.Thread(target=check).start()
    

button.when_pressed = on
button.when_released = off

pause()