"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    sensores.py

Descripción:
    Control de sensores VL53L0X mediante interfaz I2C.

    Funciones:
    - Inicialización múltiple mediante pines XSHUT.
    - Cambio de direcciones I2C.
    - Lectura continua de distancia.
    - Gestión de estados de sensores.

Versión:
    1.0.0
==============================================================================
"""

import time

import board
import busio

import adafruit_vl53l0x

from digitalio import DigitalInOut, Direction

from configuracion import (
    MAPA_SENSORES,
    SENSORES,
    EstadoSensor,
    DIRECCIONES
)

from modelos import (
    SensorARGOS,
    DireccionAudio
)

from utilidades import logger



# ==============================================================================
# CLASE CONTROLADOR DE SENSORES
# ==============================================================================


class ControladorSensores:
    """
    Administra todos los sensores VL53L0X del sistema ARGOS.
    """


    def __init__(self):

        self.i2c = busio.I2C(
            board.SCL,
            board.SDA
        )

        self.sensores = []

        self.pines_xshut = []



    # ==========================================================================
    # CONFIGURACIÓN INICIAL
    # ==========================================================================


    def preparar_pines(self):
        """
        Apaga todos los sensores mediante XSHUT.
        """

        for configuracion in MAPA_SENSORES:

            pin = DigitalInOut(
                configuracion["pin"]
            )

            pin.direction = Direction.OUTPUT

            pin.value = False

            self.pines_xshut.append(pin)



        time.sleep(
            SENSORES.TIEMPO_RESET
        )



    def iniciar_sensores(self):
        """
        Inicializa sensores uno por uno.

        Cada sensor comienza en dirección 0x29.
        Después recibe una nueva dirección.
        """

        logger.info(
            "Inicializando sensores ARGOS..."
        )


        self.preparar_pines()



        for indice, pin in enumerate(self.pines_xshut):


            configuracion = MAPA_SENSORES[indice]


            pin.value = True


            time.sleep(
                SENSORES.TIEMPO_ARRANQUE
            )


            try:

                sensor_vlx = adafruit_vl53l0x.VL53L0X(
                    self.i2c
                )


                nueva_direccion = (
                    SENSORES.DIRECCION_I2C_INICIAL
                    +
                    indice
                )


                sensor_vlx.set_address(
                    nueva_direccion
                )


                direccion_audio = DIRECCIONES[
                    configuracion["direccion"]
                ]



                sensor = SensorARGOS(

                    id=configuracion["id"],

                    pin_xshut=configuracion["pin"],

                    direccion_audio=direccion_audio,

                    direccion_i2c=nueva_direccion

                )


                sensor.estado = EstadoSensor.ACTIVO



                sensor.hardware = sensor_vlx



                self.sensores.append(
                    sensor
                )



                logger.info(
                    f"Sensor {sensor.id} listo "
                    f"direccion {hex(nueva_direccion)}"
                )



            except Exception as error:


                logger.error(
                    f"Error sensor {configuracion['id']}: {error}"
                )



    # ==========================================================================
    # LECTURA
    # ==========================================================================


    def leer_sensores(self):
        """
        Lee todos los sensores activos.

        Retorna:
            Lista de objetos SensorARGOS
        """


        for sensor in self.sensores:


            try:

                distancia = (
                    sensor.hardware.range
                )


                sensor.actualizar_distancia(
                    distancia
                )


            except Exception:


                sensor.estado = EstadoSensor.ERROR



        return self.sensores



    # ==========================================================================
    # RADAR
    # ==========================================================================


    def detectar_obstaculos(
            self,
            umbral
    ):
        """
        Actualiza el estado de detección.

        Retorna sensores con obstáculos.
        """


        encontrados = []



        for sensor in self.sensores:


            if sensor.detectar(
                umbral
            ):

                encontrados.append(
                    sensor
                )



        return encontrados



    # ==========================================================================
    # DIAGNÓSTICO
    # ==========================================================================


    def cantidad_sensores(self):

        return len(
            self.sensores
        )



    def mostrar_estado(self):

        for sensor in self.sensores:

            print(
                f"Sensor {sensor.id} | "
                f"{sensor.distancia} mm | "
                f"{sensor.direccion_audio.nombre}"
            )



# ==============================================================================
# PRUEBA DIRECTA DEL MÓDULO
# ==============================================================================


if __name__ == "__main__":


    radar = ControladorSensores()


    radar.iniciar_sensores()



    print(
        "Sensores iniciados"
    )


    try:


        while True:


            sensores = radar.leer_sensores()


            radar.mostrar_estado()


            print(
                "-" * 40
            )


            time.sleep(
                0.2
            )



    except KeyboardInterrupt:


        print(
            "Prueba terminada"
        )