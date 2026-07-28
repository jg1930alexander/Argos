"""
==============================================================================
PROYECTO ARGOS
==============================================================================

Archivo:
    main.py

Descripción:
    Punto de entrada principal del sistema ARGOS.

    Funciones:
    - Inicialización del sistema.
    - Ejecución del radar.
    - Control básico del programa.

Versión:
    1.0.0
==============================================================================
"""

from configuracion import (
    NOMBRE_PROYECTO,
    VERSION
)

from radar import RadarARGOS

from utilidades import (
    imprimir_titulo,
    imprimir_linea
)


# ==============================================================================
# INFORMACIÓN DEL SISTEMA
# ==============================================================================


def mostrar_inicio():
    """
    Muestra información del proyecto.
    """

    imprimir_titulo(
        NOMBRE_PROYECTO
    )

    print(
        f"Versión: {VERSION}"
    )

    print(
        "Detector espacial de obstáculos"
    )

    print(
        "Audio direccional para asistencia visual"
    )

    imprimir_linea()



# ==============================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================


def main():
    """
    Función principal.
    """

    mostrar_inicio()


    sistema = RadarARGOS()


    try:

        sistema.ejecutar()


    except Exception as error:

        print()

        print(
            "ERROR DEL SISTEMA:"
        )

        print(error)



# ==============================================================================
# EJECUCIÓN
# ==============================================================================


if __name__ == "__main__":

    main()