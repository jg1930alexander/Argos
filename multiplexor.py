
import board
import busio
import adafruit_tca9548a


def iniciar_i2c():
    """Inicializa y devuelve el bus I2C."""
    return busio.I2C(board.SCL, board.SDA)


def iniciar_multiplexor(i2c):
    """Inicializa y devuelve el TCA9548A."""
    return adafruit_tca9548a.TCA9548A(i2c)


def obtener_canal(multiplexor, canal):
    """Devuelve el canal solicitado del multiplexor."""
    if not 0 <= canal <= 7:
        raise ValueError("El canal debe estar entre 0 y 7.")

    return multiplexor[canal]
