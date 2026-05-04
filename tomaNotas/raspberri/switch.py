# configurar pin GPIO 14 de raspberry pi como entrada para el pulsador
import os
import time

import RPi.GPIO as GPIO

BUTTON_PIN = 14

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Usar numeración BCM de los pines
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configurar el pin 14 como entrada con resistencia pull-up


def button_callback(channel):
    button_state = GPIO.input(channel)
    if button_state == GPIO.LOW:
        print("Grabar Audio")
    else:
        print("Apagar Raspberry Pi...")
        os.system("sudo shutdown -h now")


'''def fallback_polling(channel):
    last_state = GPIO.input(channel)
    while True:
        current_state = GPIO.input(channel)
        if current_state != last_state:
            button_callback(channel)
            last_state = current_state
        time.sleep(0.05)'''

use_event_detect = False
try:
    if hasattr(GPIO, "remove_event_detect"):
        try:
            GPIO.remove_event_detect(BUTTON_PIN)
        except RuntimeError:
            pass

    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_callback, bouncetime=200)
    use_event_detect = True
    print("Usando detección de borde en GPIO 14")
except RuntimeError as exc:
    print(f"No se pudo activar la detección de borde en GPIO {BUTTON_PIN}: {exc}")
    print("Cambiando a polling con callback de software")

try:
    print("Escuchando cambios en GPIO 14. Pulse Ctrl+C para salir.")
    if not use_event_detect:
        last_state = GPIO.input(BUTTON_PIN)
        while True:
            current_state = GPIO.input(BUTTON_PIN)
            if current_state != last_state:
                button_callback(BUTTON_PIN)
                last_state = current_state
            time.sleep(1)
    else:
        while True:
            print(".")
            time.sleep(10)
except KeyboardInterrupt:
    print("Programa terminado por el usuario")
finally:
    GPIO.cleanup()  # Limpiar la configuración de los pines GPIO al finalizar el programa

