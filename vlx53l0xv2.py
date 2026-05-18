import time
import board
import busio
import adafruit_vl53l0x
from digitalio import DigitalInOut, Direction

# --- CONFIGURACIÓN DE PINES ---
# Cambia estos números de pin según tu conexión física
XSHUT_PINS = [board.D26, board.D6, board.D5] 

# Inicializar I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Lista para almacenar los objetos de los sensores ya configurados
sensores = []

def configurar_sensores():
    print("Iniciando secuencia de direccionamiento XSHUT...")
    
    # 1. Crear objetos de pin y APAGAR todos los sensores (puntos en LOW)
    pines_xshut = []
    for pin_num in XSHUT_PINS:
        pin = DigitalInOut(pin_num)
        pin.direction = Direction.OUTPUT
        pin.value = False
        pines_xshut.append(pin)
    
    # Pequeña pausa para asegurar que todos se resetearon
    time.sleep(0.1)

    # 2. Encender uno por uno y asignar nueva dirección
    for i, pin in enumerate(pines_xshut):
        # Encendemos el sensor actual
        pin.value = True
        time.sleep(0.01) # Esperar a que el sensor arranque
        
        # Al arrancar, el sensor siempre escucha en 0x29
        temp_sensor = adafruit_vl53l0x.VL53L0X(i2c)
        
        # Le cambiamos la dirección a una única (0x30, 0x31, 0x32...)
        nueva_direccion = 0x30 + i
        temp_sensor.set_address(nueva_direccion)
        
        # Lo guardamos en nuestra lista definitiva
        sensores.append(temp_sensor)
        print(f"Sensor {i+1} listo en dirección: {hex(nueva_direccion)}")

# --- EJECUCIÓN ---

try:
    configurar_sensores()
    print("-" * 40)
    print("Iniciando lecturas continuas...")
    
    while True:
        # Creamos una lista con las distancias de cada sensor
        lecturas = [s.range for s in sensores]
        
        # Formateamos la salida para que sea fácil de leer
        output = ""
        for idx, dist in enumerate(lecturas):
            # Si la distancia es > 8000, suele significar fuera de rango
            val = f"{dist:>4}mm" if dist < 8000 else "  OUT "
            output += f"S{idx+1}: {val} | "
            
        print(output)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma detenido por el usuario.")
except Exception as e:
    print(f"\nError detectado: {e}")