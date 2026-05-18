import time
import board
import busio
import adafruit_vl53l0x

# Configuración del bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializar el sensor
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

# Opcional: Ajustar el rango a "Largo" (Long Range) si es necesario
# vl53.measurement_timing_budget = 200000 

print("Iniciando lecturas...")
print("-" * 30)

try:
    while True:
        distancia = vl53.range
        
        # El VL53L0X suele marcar 8190 o 8191 mm cuando está fuera de rango
        # También verificamos que la lectura sea lógica (ej. mayor a 0)
        if distancia >= 8000:
            print("Estado: [ No se detecta objeto ]")
        else:
            print(f"Estado: [ Objeto detectado ] a {distancia} mm")
            
        time.sleep(0.2) # Un poco más de tiempo para que sea legible

except KeyboardInterrupt:
    print("\nLectura detenida por el usuario.")