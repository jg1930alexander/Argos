"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    modelos.py

Descripción:
    Contiene las estructuras de datos principales del sistema.

    Aquí se definen los objetos que representan:
    - Direcciones de audio.
    - Sensores.
    - Lecturas.
    - Estados internos.

Versión:
    1.0.0
==============================================================================
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ==============================================================================
# ESTADOS DEL SENSOR
# ==============================================================================


class EstadoSensor(Enum):
    """
    Estados posibles de un sensor VL53L0X.
    """

    INACTIVO = "INACTIVO"

    INICIALIZANDO = "INICIALIZANDO"

    ACTIVO = "ACTIVO"

    ERROR = "ERROR"


# ==============================================================================
# DIRECCIÓN ESPACIAL
# ==============================================================================


@dataclass
class DireccionAudio:
    """
    Define la posición espacial de un sonido.

    Attributes:
        nombre:
            Nombre descriptivo de la dirección.

        frecuencia:
            Frecuencia de la nota asociada.

        pan:
            Posición estéreo.
            -1 izquierda
             0 centro
             1 derecha

        profundidad:
            Posición frontal o trasera.
    """

    nombre: str

    frecuencia: float

    pan: float

    profundidad: str



# ==============================================================================
# CONFIGURACIÓN DE SENSOR
# ==============================================================================


@dataclass
class SensorConfig:
    """
    Configuración física de un sensor.

    Representa la información necesaria
    para inicializar un VL53L0X.
    """

    id: int

    pin_xshut: object

    direccion_audio: DireccionAudio



# ==============================================================================
# OBJETO SENSOR EN EJECUCIÓN
# ==============================================================================


@dataclass
class SensorARGOS:
    """
    Representa un sensor funcionando dentro del radar.

    Este objeto mantiene:
    - Configuración física.
    - Estado actual.
    - Distancia medida.
    - Actividad del audio.
    """

    id: int

    pin_xshut: object

    direccion_audio: DireccionAudio

    direccion_i2c: int = 0x30

    distancia: int = 8190

    estado: EstadoSensor = EstadoSensor.INACTIVO

    objeto_detectado: bool = False

    audio_activo: bool = False


    def actualizar_distancia(self, distancia: int):
        """
        Actualiza la lectura del sensor.
        """

        self.distancia = distancia



    def detectar(self, umbral: int) -> bool:
        """
        Determina si existe un obstáculo.

        Retorna:
            True  -> objeto detectado
            False -> libre
        """

        if self.distancia <= umbral:

            self.objeto_detectado = True

        else:

            self.objeto_detectado = False


        return self.objeto_detectado



    def activar(self):
        """
        Cambia el estado del sensor a activo.
        """

        self.estado = EstadoSensor.ACTIVO



    def detener(self):
        """
        Desactiva el sensor.
        """

        self.estado = EstadoSensor.INACTIVO

        self.audio_activo = False



# ==============================================================================
# LECTURA DEL RADAR
# ==============================================================================


@dataclass
class LecturaRadar:
    """
    Representa una lectura completa del sistema.

    Se utiliza para enviar información
    desde sensores hacia el radar y audio.
    """

    sensor_id: int

    distancia: int

    direccion: str

    detectado: bool

    timestamp: float = 0.0



# ==============================================================================
# ESTADO GENERAL DEL SISTEMA
# ==============================================================================


@dataclass
class EstadoARGOS:
    """
    Estado general del proyecto.
    """

    sensores: list[SensorARGOS] = field(default_factory=list)

    sistema_activo: bool = False


    def sensores_activos(self) -> list:
        """
        Devuelve sensores que están detectando obstáculos.
        """

        return [

            sensor

            for sensor in self.sensores

            if sensor.objeto_detectado

        ]