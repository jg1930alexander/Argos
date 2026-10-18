import time

from gpiozero import Buzzer


GPIO_BUZZER = 18
DURACION_TOTAL = 2.0
DURACION_PITIDO = 0.2
CANTIDAD_PITIDOS = 3


def pitido():
    """Mantiene encendido el buzzer activo conectado a GPIO18 durante dos segundos."""
    buzzer = Buzzer(GPIO_BUZZER)
    try:
        buzzer.on()
        time.sleep(DURACION_TOTAL)
    finally:
        buzzer.off()
        buzzer.close()


def tres_pitidos():
    """Emite tres pitidos distribuidos uniformemente en dos segundos."""
    buzzer = Buzzer(GPIO_BUZZER)
    duracion_periodo = DURACION_TOTAL / CANTIDAD_PITIDOS
    duracion_pausa = duracion_periodo - DURACION_PITIDO

    try:
        for _ in range(CANTIDAD_PITIDOS):
            buzzer.on()
            time.sleep(DURACION_PITIDO)
            buzzer.off()
            time.sleep(duracion_pausa)
    finally:
        buzzer.off()
        buzzer.close()
