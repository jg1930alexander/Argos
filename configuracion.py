"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    configuracion.py

Descripción:
    Configuración global del sistema.

IMPORTANTE

Este es el ÚNICO archivo donde deben existir constantes de configuración.

Ningún otro módulo debe contener valores "quemados" (hardcoded).

Autor:
    Alexander Jordan
Proyecto:
    ARGOS

Versión:
    1.0.0
==============================================================================
"""

from dataclasses import dataclass
from enum import Enum
import board

# ==============================================================================
# INFORMACIÓN DEL PROYECTO
# ==============================================================================

NOMBRE_PROYECTO = "Proyecto ARGOS"

VERSION = "1.0.0"

AUTOR = "Alexander Jordan"

# ==============================================================================
# CONFIGURACIÓN DEL RADAR
# ==============================================================================


@dataclass(frozen=True)
class RadarConfig:
    """
    Configuración general del radar.
    """

    # Distancia máxima para considerar un obstáculo (mm)
    DISTANCIA_UMBRAL: int = 200

    # Frecuencia de actualización del radar
    FPS: int = 20

    # Mostrar información en consola
    MOSTRAR_CONSOLA: bool = True


RADAR = RadarConfig()

# ==============================================================================
# CONFIGURACIÓN DEL AUDIO
# ==============================================================================


@dataclass(frozen=True)
class AudioConfig:
    """
    Configuración del motor de audio.
    """

    SAMPLE_RATE: int = 44100

    VOLUMEN_GENERAL: float = 0.40

    # Tamaño del filtro utilizado para simular sonido trasero.
    TAMANO_FILTRO: int = 5

    # Cantidad de muestras de retraso para el eco.
    DELAY_BACK: int = 80

    # Intensidad del eco.
    ECO_BACK: float = 0.30

    # Número de canales.
    CANALES: int = 2


AUDIO = AudioConfig()

# ==============================================================================
# CONFIGURACIÓN DE LOS SENSORES
# ==============================================================================


@dataclass(frozen=True)
class SensorConfig:
    """
    Configuración general de los VL53L0X.
    """

    NUMERO_SENSORES: int = 6

    DIRECCION_I2C_INICIAL: int = 0x30

    TIEMPO_RESET: float = 0.10

    TIEMPO_ARRANQUE: float = 0.01


SENSORES = SensorConfig()

# ==============================================================================
# ESTADO DEL SENSOR
# ==============================================================================


class EstadoSensor(Enum):
    """
    Estado lógico del sensor.
    """

    INACTIVO = 0

    ACTIVO = 1

    ERROR = 2


# ==============================================================================
# DIRECCIÓN ESPACIAL
# ==============================================================================


@dataclass(frozen=True)
class DireccionAudio:
    """
    Representa una dirección espacial.
    """

    nombre: str

    frecuencia: float

    pan: float

    profundidad: str


# ==============================================================================
# MAPA DE DIRECCIONES
# ==============================================================================

"""
Las teclas ya NO representan teclas del teclado.

Ahora únicamente representan un identificador interno.

Esto permite cambiar las notas sin modificar el resto del proyecto.
"""

DIRECCIONES = {

    # ==========================
    # FRENTE
    # ==========================

    "a": DireccionAudio(
        nombre="Frente Izquierda",
        frecuencia=261.63,
        pan=-1.0,
        profundidad="front"
    ),

    "s": DireccionAudio(
        nombre="Frente Centro Izquierda",
        frecuencia=329.63,
        pan=-0.5,
        profundidad="front"
    ),

    "d": DireccionAudio(
        nombre="Frente Centro Derecha",
        frecuencia=392.00,
        pan=0.5,
        profundidad="front"
    ),

    "f": DireccionAudio(
        nombre="Frente Derecha",
        frecuencia=493.88,
        pan=1.0,
        profundidad="front"
    ),

    # ==========================
    # ATRÁS
    # ==========================

    "z": DireccionAudio(
        nombre="Atrás Izquierda",
        frecuencia=261.63,
        pan=-1.0,
        profundidad="back"
    ),

    "x": DireccionAudio(
        nombre="Atrás Centro Izquierda",
        frecuencia=329.63,
        pan=-0.5,
        profundidad="back"
    ),

    "c": DireccionAudio(
        nombre="Atrás Centro Derecha",
        frecuencia=392.00,
        pan=0.5,
        profundidad="back"
    ),

    "v": DireccionAudio(
        nombre="Atrás Derecha",
        frecuencia=493.88,
        pan=1.0,
        profundidad="back"
    )

}

# ==============================================================================
# CONFIGURACIÓN FÍSICA DE LOS SENSORES
# ==============================================================================

"""
IMPORTANTE

El orden de esta lista debe ser EXACTAMENTE el mismo
que el orden físico de los sensores instalados.

Actualmente:

Sensor 1 -> A

Sensor 2 -> S

Sensor 3 -> D

Cuando agregues los demás sensores únicamente
descomenta las líneas correspondientes.
"""

MAPA_SENSORES = [

    {
        "id": 1,
        "pin": board.D26,
        "direccion": "a"
    },

    {
        "id": 2,
        "pin": board.D6,
        "direccion": "s"
    },

    {
        "id": 3,
        "pin": board.D5,
        "direccion": "d"
    },

    # ============================
    # FUTUROS SENSORES
    # ============================

    # {
    #     "id":4,
    #     "pin":board.DXX,
    #     "direccion":"f"
    # },

    # {
    #     "id":5,
    #     "pin":board.DXX,
    #     "direccion":"z"
    # },

    # {
    #     "id":6,
    #     "pin":board.DXX,
    #     "direccion":"x"
    # },

    # {
    #     "id":7,
    #     "pin":board.DXX,
    #     "direccion":"c"
    # },

    # {
    #     "id":8,
    #     "pin":board.DXX,
    #     "direccion":"v"
    # }

]

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================


def obtener_direccion(nombre: str) -> DireccionAudio:
    """
    Devuelve la configuración completa de una dirección.

    Ejemplo

    direccion = obtener_direccion("a")

    direccion.frecuencia

    direccion.pan

    direccion.nombre
    """

    return DIRECCIONES[nombre]


def obtener_sensor(sensor_id: int) -> dict:
    """
    Devuelve la configuración de un sensor físico.
    """

    for sensor in MAPA_SENSORES:

        if sensor["id"] == sensor_id:

            return sensor

    raise ValueError(f"No existe el sensor {sensor_id}")