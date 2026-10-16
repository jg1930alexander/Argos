"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    utilidades.py

Descripción:
    Funciones auxiliares generales utilizadas por los módulos del sistema.

Versión:
    1.0.0
==============================================================================
"""

import logging
import time
from datetime import datetime


# ==============================================================================
# CONFIGURACIÓN DE LOGS
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("ARGOS")


# ==============================================================================
# CONSOLA
# ==============================================================================


def imprimir_titulo(texto: str):
    """
    Imprime un título de sección.
    """

    print()
    print("=" * 60)
    print(texto.center(60))
    print("=" * 60)



def imprimir_linea():
    """
    Imprime una línea separadora.
    """

    print("-" * 60)



def mensaje_inicio():
    """
    Muestra información inicial del sistema.
    """

    imprimir_titulo("PROYECTO ARGOS")

    print("Sistema de detección espacial activo")
    print()



# ==============================================================================
# TIEMPO
# ==============================================================================


def esperar(segundos: float):
    """
    Pausa la ejecución.
    """

    time.sleep(segundos)



def tiempo_actual():
    """
    Devuelve la hora actual.
    """

    return datetime.now().strftime("%H:%M:%S")



# ==============================================================================
# DISTANCIAS
# ==============================================================================


def distancia_valida(distancia: int) -> bool:
    """
    Comprueba si la lectura del VL53L0X es válida.

    Los sensores suelen entregar valores altos
    cuando no existe un objeto dentro del rango.
    """

    return distancia < 8000



def distancia_texto(distancia: int) -> str:
    """
    Convierte una distancia en texto.
    """

    if distancia_valida(distancia):

        return f"{distancia} mm"

    return "FUERA DE RANGO"



# ==============================================================================
# AUDIO
# ==============================================================================


def calcular_volumen(
        distancia: int,
        distancia_maxima: int
) -> float:
    """
    Calcula volumen según proximidad.

    Más cerca:
        Mayor volumen.

    Más lejos:
        Menor volumen.

    Retorna:
        Valor entre 0.0 y 1.0
    """

    if distancia >= distancia_maxima:

        return 0.0


    volumen = 1 - (distancia / distancia_maxima)


    if volumen < 0:

        volumen = 0


    if volumen > 1:

        volumen = 1


    return volumen



# ==============================================================================
# DIAGNÓSTICO
# ==============================================================================


def mostrar_sensor(sensor):
    """
    Muestra información de un sensor individual.
    """

    print(
        f"Sensor {sensor.id} | "
        f"{sensor.direccion_audio.nombre} | "
        f"{distancia_texto(sensor.distancia)} | "
        f"{sensor.estado.value}"
    )



def mostrar_sensores(lista_sensores):
    """
    Muestra el estado de todos los sensores.
    """

    imprimir_linea()

    print("ESTADO DE SENSORES")

    imprimir_linea()


    for sensor in lista_sensores:

        mostrar_sensor(sensor)


    imprimir_linea()