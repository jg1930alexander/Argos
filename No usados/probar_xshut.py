import time
import board
from digitalio import DigitalInOut, Direction

PINES = [
    board.D26,
    board.D19,
    board.D13,
    board.D6,
    board.D21,
    board.D20,
    board.D16,
    board.D12
]

gpio = []

for pin in PINES:
    p = DigitalInOut(pin)
    p.direction = Direction.OUTPUT
    gpio.append(p)

while True:

    print("TODOS OFF")

    for p in gpio:
        p.value = False

    time.sleep(3)

    print("TODOS ON")

    for p in gpio:
        p.value = True

    time.sleep(3)