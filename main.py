
import time

from multiplexor import iniciar_i2c, iniciar_multiplexor
from sensores import iniciar_sensores, leer_todos, mostrar_distancias


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
    """Inicializa el hardware y ejecuta la prueba."""
    i2c = iniciar_i2c()

    try:
        multiplexor = iniciar_multiplexor(i2c)
        sensores = iniciar_sensores(multiplexor)

        if sensores:
            ejecutar_prueba(sensores)
        else:
            print("No se inicializó ningún sensor.")

    finally:
        i2c.deinit()
        print("Bus I2C cerrado.")


if __name__ == "__main__":
    main()
