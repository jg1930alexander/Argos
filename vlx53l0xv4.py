import time
import board
import busio
import adafruit_vl53l0x
import pygame
from digitalio import DigitalInOut, Direction

# --- CONFIGURACIÓN DE AUDIO ---
pygame.mixer.init()
sonidos = [
    pygame.mixer.Sound("audio1.mp3"),
    pygame.mixer.Sound("audio2.mp3"),
    pygame.mixer.Sound("audio3.mp3")
]

# Creamos canales dedicados para cada sensor
canales = [pygame.mixer.Channel(i) for i in range(len(sonidos))]

# Rango de acción en milímetros
DIST_MIN = 50   # Máximo volumen (1.0)
DIST_MAX = 500  # Mínimo volumen (0.0)

# --- CONFIGURACIÓN DE SENSORES (Igual al anterior) ---
XSHUT_PINS = [board.D26, board.D6, board.D5] 
i2c = busio.I2C(board.SCL, board.SDA)
sensores = []

def configurar_sensores():
    pines_xshut = []
    for pin_num in XSHUT_PINS:
        pin = DigitalInOut(pin_num)
        pin.direction = Direction.OUTPUT
        pin.value = False
        pines_xshut.append(pin)
    time.sleep(0.1)
    for i, pin in enumerate(pines_xshut):
        pin.value = True
        time.sleep(0.01)
        temp_sensor = adafruit_vl53l0x.VL53L0X(i2c)
        temp_sensor.set_address(0x30 + i)
        sensores.append(temp_sensor)

# --- FUNCIÓN PARA CALCULAR VOLUMEN ---
def calcular_volumen(distancia):
    """Mapea la distancia a un valor entre 0.0 y 1.0"""
    if distancia < DIST_MIN: return 1.0
    if distancia > DIST_MAX: return 0.0
    
    # Regla de tres inversa: (Max - Actual) / (Max - Min)
    vol = (DIST_MAX - distancia) / (DIST_MAX - DIST_MIN)
    return round(vol, 2)

# --- EJECUCIÓN ---
try:
    configurar_sensores()
    
    while True:
        for i, s in enumerate(sensores):
            dist = s.range
            
            if dist < DIST_MAX:
                vol = calcular_volumen(dist)
                
                # Si no se está reproduciendo, iniciamos el loop
                if not canales[i].get_busy():
                    canales[i].play(sonidos[i], loops=-1) # loops=-1 para sonido infinito
                
                # Ajustamos el volumen en tiempo real
                canales[i].set_volume(vol)
            else:
                # Si el objeto sale del rango, bajamos volumen o paramos
                canales[i].fadeout(500) # Se apaga suavemente en 500ms
                
        time.sleep(0.05)

except KeyboardInterrupt:
    pygame.mixer.quit()