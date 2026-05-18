import time
import board
import busio
import adafruit_vl53l0x
import pygame  # Librería para audio
from digitalio import DigitalInOut, Direction

# --- CONFIGURACIÓN DE AUDIO ---
pygame.mixer.init()
# Asegúrate de que estos archivos estén en la misma carpeta que tu script
sonidos = [
    pygame.mixer.Sound("audio1.mp3"),
    pygame.mixer.Sound("audio2.mp3"),
    pygame.mixer.Sound("audio3.mp3")
]

# Umbral de detección en milímetros (ajusta según necesites)
UMBRAL_DISTANCIA = 200 

# Para evitar que el audio se repita en cada ciclo del bucle
sonido_reproduciendo = [False, False, False]

# --- CONFIGURACIÓN DE PINES Y SENSORES ---
XSHUT_PINS = [board.D26, board.D6, board.D5] 
i2c = busio.I2C(board.SCL, board.SDA)
sensores = []

def configurar_sensores():
    print("Iniciando secuencia de direccionamiento XSHUT...")
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
        nueva_direccion = 0x30 + i
        temp_sensor.set_address(nueva_direccion)
        sensores.append(temp_sensor)
        print(f"Sensor {i+1} listo en dirección: {hex(nueva_direccion)}")

# --- EJECUCIÓN ---

try:
    configurar_sensores()
    print("Sistema listo. Esperando detección...")
    
    while True:
        output = ""
        for i, s in enumerate(sensores):
            distancia = s.range
            
            # Lógica de detección y audio
            if distancia < UMBRAL_DISTANCIA:
                if not sonido_reproduciendo[i]:
                    print(f"¡Objeto detectado en Sensor {i+1}!")
                    sonidos[i].play()
                    sonido_reproduciendo[i] = True
            else:
                # Resetear la bandera cuando el objeto se aleja
                sonido_reproduciendo[i] = False

            val = f"{distancia:>4}mm" if distancia < 8000 else "  OUT "
            output += f"S{i+1}: {val} | "
            
        print(output)
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nPrograma detenido.")