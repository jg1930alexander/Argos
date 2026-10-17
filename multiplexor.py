
import board
import busio
import adafruit_tca9548a


def iniciar_i2c():
    """Inicializa y devuelve el bus I2C."""
    return busio.I2C(board.SCL, board.SDA)#inicializa el bus I2C utilizando los pines SCL y SDA de la placa y devuelve el objeto I2C para su uso posterior


def iniciar_multiplexor(i2c):
    """Inicializa y devuelve el TCA9548A."""
    return adafruit_tca9548a.TCA9548A(i2c)#inicializa el multiplexor TCA9548A utilizando el bus I2C proporcionado y devuelve el objeto del multiplexor para su uso posterior


def obtener_canal(multiplexor, canal):#inicializa la función que devuelve el canal solicitado del multiplexor
    """Devuelve el canal solicitado del multiplexor."""
    if not 0 <= canal <= 7:#si el canal solicitado no está entre 0 y 7, se lanza una excepción indicando que el canal es inválido
        raise ValueError("El canal debe estar entre 0 y 7.")

    return multiplexor[canal]#devuelve el canal solicitado del multiplexor, que permite acceder a los dispositivos conectados a ese canal específico
