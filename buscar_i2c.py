import time
import board
import busio
import adafruit_vl53l0x
from digitalio import DigitalInOut, Direction

XSHUT_PINS = [
    board.D26,
    board.D19,
    board.D13,
    board.D5,
    board.D21,
    board.D20,
    board.D16,
    board.D12
]

DIRECCION_BASE = 0x30

print("Iniciando I2C...")

i2c = busio.I2C(board.SCL, board.SDA)

# Apagar todos
xshut = []

for pin in XSHUT_PINS:
    p = DigitalInOut(pin)
    p.direction = Direction.OUTPUT
    p.value = False
    xshut.append(p)

time.sleep(0.2)

sensores = []

print("Inicializando sensores...")

for i, pin in enumerate(xshut):

    pin.value = True
    time.sleep(0.05)

    try:

        sensor = adafruit_vl53l0x.VL53L0X(i2c)

        direccion = DIRECCION_BASE + i

        sensor.set_address(direccion)

        sensores.append(sensor)

        print(f"Sensor {i+1} OK -> {hex(direccion)}")

    except Exception as e:

        sensores.append(None)

        print(f"Sensor {i+1} ERROR -> {e}")

print("\nLectura continua...\n")

contador = 0

while True:

    contador += 1

    print(f"\n--------------- CICLO {contador} ---------------")

    for i, sensor in enumerate(sensores):

        if sensor is None:

            print(f"S{i+1}: NO INICIALIZADO")

            continue

        try:

            distancia = sensor.range

            print(f"S{i+1}: {distancia} mm")

        except Exception as e:

            print(f"S{i+1}: ERROR -> {e}")

    time.sleep(1)