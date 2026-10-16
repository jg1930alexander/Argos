
import time

from multiplexor import iniciar_i2c, iniciar_multiplexor
from sensores import iniciar_sensores, leer_todos, mostrar_distancias

from audio import iniciar_audio, actualizar_audio, cerrar_audio
from audifonos import esperar_audifonos


# Configuración
INTERVALO = 0.1       # Tiempo entre lecturas, en segundos
UMBRAL_MM = 1000      # Distancia de detección: 1 metro

def ejecutar_argos(sensores):
    """Lee los sensores y actualiza el audio direccional."""

    try:
        while True:
            distancias = leer_todos(sensores)

            # Mostrar las distancias detectadas
            mostrar_distancias(distancias)

            # Activar las notas según los obstáculos
            actualizar_audio(distancias, umbral_mm=UMBRAL_MM)

            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        print("\nARGOS detenido por el usuario.")

def ejecutar_prueba(sensores, intervalo=0.5):
    """Lee y muestra las distancias continuamente."""
    try:
        while True:
            distancias = leer_todos(sensores)
            mostrar_distancias(distancias)
            print("-" * 20)
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\nPrueba detenida por el usuario.")


def main():
    """Inicializa el hardware, los sensores y el audio."""

    esperar_audifonos()

    i2c = iniciar_i2c()
    audio_iniciado = False

    try:
        multiplexor = iniciar_multiplexor(i2c)
        sensores = iniciar_sensores(multiplexor)

        if not sensores:
            print("No se inicializaron los sensores.")
            return

        iniciar_audio()
        audio_iniciado = True

        print("ARGOS funcionando. Presiona Ctrl+C para detenerlo.")
        ejecutar_argos(sensores)

    finally:
        if audio_iniciado:
            cerrar_audio()

        i2c.deinit()
        print("Bus I2C cerrado.")


if __name__ == "__main__":
    main()
