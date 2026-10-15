import time, board, busio
import adafruit_tca9548a, adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)

sensores = {}
for ch in range(8):
    try:
        sensores[ch] = adafruit_vl53l0x.VL53L0X(tca[ch])
        print(f"Canal {ch}: OK")
    except Exception as e:
        print(f"Canal {ch}: sin sensor ({e})")

while True:
    for ch, s in sensores.items():
        print(f"Canal {ch}: {s.range} mm")
    print("-" * 20)
    time.sleep(0.5)