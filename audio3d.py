"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    audio3d.py

Descripción:
    Motor de audio espacial de ARGOS.

    Genera sonidos direccionales utilizando:
    - Frecuencias asignadas a cada dirección.
    - Paneo estéreo izquierda/derecha.
    - Simulación frontal/trasera.
    - Control dinámico de volumen.

Versión:
    1.0.0
==============================================================================
"""

import numpy as np
import sounddevice as sd
import threading

from configuracion import AUDIO
from modelos import SensorARGOS


# ==============================================================================
# CLASE MOTOR DE AUDIO 3D
# ==============================================================================


class MotorAudio3D:
    """
    Motor encargado de generar el audio espacial.

    No controla sensores directamente.
    Recibe estados de sensores y genera sonido.
    """

    def __init__(self):

        self.sensores_activos = {}

        self.fase = 0

        self.ejecutando = False

        self.lock = threading.Lock()



    # ==========================================================================
    # CONTROL DE SENSORES
    # ==========================================================================


    def activar_sensor(self, sensor: SensorARGOS):
        """
        Activa el sonido asociado a un sensor.
        """

        with self.lock:

            self.sensores_activos[sensor.id] = sensor



    def desactivar_sensor(self, sensor_id: int):
        """
        Elimina un sensor del motor de audio.
        """

        with self.lock:

            if sensor_id in self.sensores_activos:

                del self.sensores_activos[sensor_id]



    def limpiar(self):
        """
        Apaga todos los sonidos.
        """

        with self.lock:

            self.sensores_activos.clear()



    # ==========================================================================
    # GENERACIÓN DE AUDIO
    # ==========================================================================


    def aplicar_efecto_trasero(
            self,
            onda
    ):
        """
        Simula que el sonido viene desde atrás.

        Aplica:
        - Reducción de volumen.
        - Filtro simple.
        - Eco.
        """

        onda = onda * 0.5


        filtro = np.ones(
            AUDIO.TAMANO_FILTRO
        ) / AUDIO.TAMANO_FILTRO


        onda = np.convolve(
            onda,
            filtro,
            mode="same"
        )


        delay = min(
            AUDIO.DELAY_BACK,
            len(onda)-1
        )


        eco = np.roll(
            onda,
            delay
        )


        onda = onda + (
            eco *
            AUDIO.ECO_BACK
        )


        return onda



    def callback(
            self,
            outdata,
            frames,
            tiempo,
            estado
    ):
        """
        Función llamada automáticamente
        por sounddevice.
        """

        tiempo_audio = (
            np.arange(frames)
            +
            self.fase
        ) / AUDIO.SAMPLE_RATE



        izquierda = np.zeros(frames)

        derecha = np.zeros(frames)



        with self.lock:

            sensores = list(
                self.sensores_activos.values()
            )



        for sensor in sensores:


            direccion = sensor.direccion_audio


            frecuencia = direccion.frecuencia


            onda = np.sin(
                2 *
                np.pi *
                frecuencia *
                tiempo_audio
            )


            # --------------------------
            # PROFUNDIDAD
            # --------------------------

            if direccion.profundidad == "back":

                onda = self.aplicar_efecto_trasero(
                    onda
                )



            # --------------------------
            # DISTANCIA
            # --------------------------

            distancia = sensor.distancia


            volumen_distancia = max(

                0.1,

                1 -
                (
                    distancia /
                    2000
                )

            )


            onda *= volumen_distancia



            # --------------------------
            # PANEO
            # --------------------------

            pan = direccion.pan


            ganancia_izquierda = (
                1 - pan
            ) / 2


            ganancia_derecha = (
                1 + pan
            ) / 2



            izquierda += (
                onda *
                ganancia_izquierda
            )


            derecha += (
                onda *
                ganancia_derecha
            )



        cantidad = len(sensores)



        if cantidad > 0:

            izquierda /= cantidad

            derecha /= cantidad



        salida = np.column_stack(
            (
                izquierda,
                derecha
            )
        )


        outdata[:] = (
            salida *
            AUDIO.VOLUMEN_GENERAL
        )


        self.fase += frames



    # ==========================================================================
    # INICIO Y DETENCIÓN
    # ==========================================================================


    def iniciar(self):
        """
        Inicia el stream de audio.
        """

        if self.ejecutando:

            return


        self.ejecutando = True



        self.stream = sd.OutputStream(

            channels=AUDIO.CANALES,

            samplerate=AUDIO.SAMPLE_RATE,

            callback=self.callback

        )


        self.stream.start()



    def detener(self):
        """
        Detiene el audio.
        """

        if not self.ejecutando:

            return


        self.stream.stop()

        self.stream.close()

        self.ejecutando = False



# ==============================================================================
# PRUEBA DIRECTA
# ==============================================================================


if __name__ == "__main__":

    print(
        "Motor Audio 3D ARGOS"
    )

    motor = MotorAudio3D()

    motor.iniciar()


    print(
        "Audio iniciado"
    )


    try:

        while True:

            pass


    except KeyboardInterrupt:

        motor.detener()

        print(
            "Audio detenido"
        )