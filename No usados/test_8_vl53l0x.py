#!/usr/bin/env python3
"""
===========================================================
PROYECTO ARGOS
Prueba de 8 sensores VL53L0X
===========================================================

GPIO utilizados:

Sensor 1 -> GPIO26
Sensor 2 -> GPIO19
Sensor 3 -> GPIO13
Sensor 4 -> GPIO6
Sensor 5 -> GPIO21
Sensor 6 -> GPIO20
Sensor 7 -> GPIO16
Sensor 8 -> GPIO12
"""

import time

import board
import busio
import adafruit_vl53l0x

from digitalio import DigitalInOut, Direction

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------

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

DIRECCION_INICIAL = 0x30

# ---------------------------------------------------------
# I2C
# ---------------------------------------------------------

i2c = busio.I2C(board.SCL, board.SDA)

# ---------------------------------------------------------
# APAGAR TODOS LOS SENSORES
# ---------------------------------------------------------

print("\nApagando todos los sensores...")

pines = []

for pin in XSHUT_PINS:

    salida = DigitalInOut(pin)

    salida.direction = Direction.OUTPUT

    salida.value = False

    pines.append(salida)

time.sleep(0.2)

# ---------------------------------------------------------
# ENCENDER UNO POR UNO
# ---------------------------------------------------------

sensores = []

print("Asignando direcciones...\n")

for i, pin in enumerate(pines):

    pin.value = True

    time.sleep(0.05)

    sensor = adafruit_vl53l0x.VL53L0X(i2c)

    direccion = DIRECCION_INICIAL + i

    sensor.set_address(direccion)

    sensores.append(sensor)

    print(
        f"Sensor {i+1} -> "
        f"GPIO {XSHUT_PINS[i]} -> "
        f"{hex(direccion)}"
    )

print("\nTodos los sensores inicializados correctamente.")

print("\nPresiona CTRL+C para salir.\n")

# ---------------------------------------------------------
# LECTURA CONTINUA
# ---------------------------------------------------------

try:

    while True:

        print("=" * 70)

        for i, sensor in enumerate(sensores):

            try:

                distancia = sensor.range

                if distancia >= 8000:

                    texto = "OUT"

                else:

                    texto = f"{distancia} mm"

                print(
                    f"Sensor {i+1:<2} "
                    f"Direccion {hex(0x30+i)} "
                    f"Distancia: {texto}"
                )

            except Exception as e:

                print(
                    f"Sensor {i+1} ERROR -> {e}"
                )

        time.sleep(1.0)

except KeyboardInterrupt:

    print("\nPrueba finalizada.")