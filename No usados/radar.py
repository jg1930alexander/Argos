"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    radar.py

Descripción:
    Lógica principal del radar ARGOS.

    Se encarga de:
    - Coordinar sensores.
    - Detectar obstáculos.
    - Enviar información al motor de audio.
    - Gestionar activación/desactivación de sonidos.

Versión:
    1.0.0
==============================================================================
"""

import time

from configuracion import RADAR

from sensores import ControladorSensores

from audio3d import MotorAudio3D

from utilidades import (
    logger,
    mostrar_sensores
)


# ==============================================================================
# CLASE RADAR ARGOS
# ==============================================================================


class RadarARGOS:
    """
    Controlador principal del sistema ARGOS.
    """


    def __init__(self):

        self.sensores = ControladorSensores()

        self.audio = MotorAudio3D()

        self.funcionando = False



    # ==========================================================================
    # INICIALIZACIÓN
    # ==========================================================================


    def iniciar(self):
        """
        Inicializa sensores y audio.
        """

        logger.info(
            "Iniciando Proyecto ARGOS..."
        )


        self.sensores.iniciar_sensores()


        self.audio.iniciar()


        self.funcionando = True


        logger.info(
            "ARGOS listo"
        )



    # ==========================================================================
    # PROCESAMIENTO DEL RADAR
    # ==========================================================================


    def actualizar(self):
        """
        Realiza un ciclo completo:

        1. Lee sensores.
        2. Detecta obstáculos.
        3. Actualiza audio.
        """


        lista_sensores = (
            self.sensores.leer_sensores()
        )


        obstaculos = (
            self.sensores.detectar_obstaculos(
                RADAR.DISTANCIA_UMBRAL
            )
        )


        sensores_detectados = set()



        for sensor in obstaculos:


            sensores_detectados.add(
                sensor.id
            )


            if not sensor.audio_activo:


                self.audio.activar_sensor(
                    sensor
                )


                sensor.audio_activo = True



        # Apagar sonidos cuando desaparece objeto

        for sensor in lista_sensores:


            if (

                sensor.audio_activo

                and

                sensor.id not in sensores_detectados

            ):


                self.audio.desactivar_sensor(
                    sensor.id
                )


                sensor.audio_activo = False



        if RADAR.MOSTRAR_CONSOLA:


            mostrar_sensores(
                lista_sensores
            )



    # ==========================================================================
    # BUCLE PRINCIPAL
    # ==========================================================================


    def ejecutar(self):
        """
        Mantiene el radar funcionando.
        """


        self.iniciar()



        try:


            while self.funcionando:


                inicio = time.time()



                self.actualizar()



                tiempo_ciclo = (
                    time.time()
                    -
                    inicio
                )


                espera = (

                    1 / RADAR.FPS

                ) - tiempo_ciclo



                if espera > 0:

                    time.sleep(
                        espera
                    )



        except KeyboardInterrupt:


            logger.info(
                "Deteniendo ARGOS..."
            )


            self.detener()



    # ==========================================================================
    # DETENER SISTEMA
    # ==========================================================================


    def detener(self):
        """
        Apaga el sistema.
        """


        self.funcionando = False


        self.audio.detener()


        logger.info(
            "Sistema detenido"
        )



# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================


if __name__ == "__main__":


    argos = RadarARGOS()


    argos.ejecutar()