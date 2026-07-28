"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    pruebas.py

Descripción:
    Módulo de pruebas independientes.

    Permite comprobar:
    - Audio espacial.
    - Sensores VL53L0X.
    - Comunicación general del sistema.

Versión:
    1.0.0
==============================================================================
"""

import time

from configuracion import DIRECCIONES

from modelos import SensorARGOS

from audio3d import MotorAudio3D

from sensores import ControladorSensores

from utilidades import (
    imprimir_titulo,
    imprimir_linea,
    esperar
)



# ==============================================================================
# PRUEBA DE AUDIO
# ==============================================================================


def prueba_audio():
    """
    Prueba todas las direcciones de audio.

    No requiere sensores conectados.
    """

    imprimir_titulo(
        "PRUEBA AUDIO 3D ARGOS"
    )


    motor = MotorAudio3D()

    motor.iniciar()


    print(
        "Probando direcciones..."
    )


    for clave, direccion in DIRECCIONES.items():


        print(
            f"Probando {clave}: "
            f"{direccion.nombre}"
        )


        sensor_prueba = SensorARGOS(

            id=0,

            pin_xshut=None,

            direccion_audio=direccion,

            distancia=500

        )


        motor.activar_sensor(
            sensor_prueba
        )


        esperar(1)


        motor.desactivar_sensor(
            0
        )


    motor.detener()


    print(
        "Prueba de audio finalizada"
    )



# ==============================================================================
# PRUEBA DE SENSORES
# ==============================================================================


def prueba_sensores():
    """
    Prueba inicialización y lectura
    de sensores VL53L0X.
    """

    imprimir_titulo(
        "PRUEBA SENSORES VL53L0X"
    )


    controlador = ControladorSensores()


    controlador.iniciar_sensores()


    print(
        "Sensores detectados:",
        controlador.cantidad_sensores()
    )


    try:


        while True:


            sensores = (
                controlador.leer_sensores()
            )


            imprimir_linea()


            for sensor in sensores:


                print(

                    f"Sensor {sensor.id} | "

                    f"{sensor.direccion_audio.nombre} | "

                    f"{sensor.distancia} mm"

                )


            time.sleep(
                0.5
            )


    except KeyboardInterrupt:


        print(
            "Prueba detenida"
        )



# ==============================================================================
# PRUEBA COMPLETA
# ==============================================================================


def prueba_completa():
    """
    Ejecuta el sistema completo ARGOS.
    """

    imprimir_titulo(
        "PRUEBA COMPLETA ARGOS"
    )


    from radar import RadarARGOS


    sistema = RadarARGOS()


    sistema.ejecutar()



# ==============================================================================
# MENÚ
# ==============================================================================


def menu_pruebas():


    while True:


        imprimir_titulo(
            "MENU PRUEBAS ARGOS"
        )


        print(
            """
1 - Probar audio 3D

2 - Probar sensores

3 - Ejecutar radar completo

4 - Salir
"""
        )


        opcion = input(
            "Seleccione opción: "
        )


        if opcion == "1":

            prueba_audio()



        elif opcion == "2":

            prueba_sensores()



        elif opcion == "3":

            prueba_completa()



        elif opcion == "4":

            break



        else:

            print(
                "Opción inválida"
            )



# ==============================================================================
# EJECUCIÓN
# ==============================================================================


if __name__ == "__main__":

    menu_pruebas()
