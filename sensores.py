
import adafruit_vl53l0x


def iniciar_sensores(multiplexor):
    """Inicializa los sensores disponibles en los ocho canales."""
    sensores = {}

    for canal in range(8):
        try:
            bus_canal = multiplexor[canal]
            sensores[canal] = adafruit_vl53l0x.VL53L0X(
                bus_canal
            )
            print(f"Canal {canal}: sensor OK")

        except Exception as error:
            print(f"Canal {canal}: error al iniciar: {error}")

    return sensores


def leer_distancia(sensor):
    """Devuelve la distancia medida en milímetros."""
    try:
        return sensor.range
    except Exception as error:
        print(f"Error leyendo sensor: {error}")
        return None


def leer_todos(sensores):
    """Devuelve un diccionario con las distancias actuales."""
    distancias = {}

    for canal, sensor in sensores.items():
        distancias[canal] = leer_distancia(sensor)

    return distancias


def mostrar_distancias(distancias):
    """Muestra las distancias disponibles."""
    for canal, distancia in distancias.items():
        if distancia is None:
            print(f"Canal {canal}: sin lectura")
        else:
            print(f"Canal {canal}: {distancia} mm")
