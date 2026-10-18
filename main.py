
import time
from buzzer import pitido, tres_pitidos
from multiplexor import iniciar_i2c, iniciar_multiplexor
from sensores import iniciar_sensores, leer_todos, mostrar_distancias
from audio import iniciar_audio, actualizar_audio, cerrar_audio
from audifonos import esperar_audifonos


# Configuración
INTERVALO = 0.1       # Tiempo entre lecturas, en segundos
UMBRAL_MM = 1000      # Distancia de detección: 1 metro

def ejecutar_argos(sensores):
    """Lee los sensores y actualiza el audio direccional."""

    try:#intenta ejecutar el bucle principal del programa, que lee los sensores y actualiza el audio direccional
        while True:
            distancias = leer_todos(sensores)#lee las distancias de todos los sensores y las almacena en un diccionario

            mostrar_distancias(distancias)#imprime las distancias detectadas por los sensores en la consola

            # Activar las notas según los obstáculos
            actualizar_audio(distancias, umbral_mm=UMBRAL_MM)#actualiza el audio direccional según las distancias detectadas por los sensores y el umbral de detección

            time.sleep(INTERVALO)#espera un tiempo definido por la variable INTERVALO antes de volver a leer los sensores y actualizar el audio direccional

    except KeyboardInterrupt:#si el usuario presiona Ctrl+C, se interrumpe el bucle y se imprime un mensaje indicando que el programa ha sido detenido
        print("\nARGOS detenido por el usuario.")


def main():
    """Inicializa el hardware, los sensores y el audio."""
    pitido()#emite un pitido de inicio para indicar que el programa ha comenzado
    esperar_audifonos()#espera a que los audífonos KVIDIO 201 estén conectados y sean la salida activa

    i2c = iniciar_i2c() #inicializa el bus I2C
    audio_iniciado = False#inicializa la variable de control del audio

    try:
        multiplexor = iniciar_multiplexor(i2c)#inicializa el multiplexor TCA9548A
        sensores = iniciar_sensores(multiplexor)#inicializa los sensores de distancia

        if not sensores:#si no se inicializaron los sensores, imprime un mensaje y termina la ejecución
            print("No se inicializaron los sensores.")
            return

        iniciar_audio()#inicializa el audio direccional
        audio_iniciado = True#indica que el audio se ha iniciado correctamente

        tres_pitidos()#emite tres pitidos para indicar que el programa está listo para funcionar
        print("ARGOS funcionando. Presiona Ctrl+C para detenerlo.")#indica que el programa está en funcionamiento y cómo detenerlo
        ejecutar_argos(sensores)#ejecuta la función principal que lee los sensores y actualiza el audio direccional

    finally:#si ocurre una excepción o se interrumpe el programa, se ejecuta este bloque para cerrar el audio y el bus I2C
        if audio_iniciado:#si el audio se inició correctamente, se cierra
            cerrar_audio()

        i2c.deinit()#desinicializa el bus I2C
        print("Bus I2C cerrado.")


if __name__ == "__main__":#si el archivo se ejecuta directamente, se llama a la función main() para iniciar el programa
    main()
