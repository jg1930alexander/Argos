
import adafruit_vl53l0x


def iniciar_sensores(multiplexor):#inicializa la función que devuelve un diccionario con los sensores disponibles en los ocho canales del multiplexor
    """Inicializa los sensores disponibles en los ocho canales."""
    sensores = {}#inicializa un diccionario vacío para almacenar los sensores disponibles en los ocho canales del multiplexor

    for canal in range(8):#itera sobre los ocho canales del multiplexor (0 a 7) para intentar inicializar un sensor en cada canal
        try:#intenta inicializar un sensor en el canal actual del multiplexor
            bus_canal = multiplexor[canal]#obtiene el bus I2C correspondiente al canal actual del multiplexor
            sensores[canal] = adafruit_vl53l0x.VL53L0X(bus_canal)#inicializa un sensor VL53L0X en el bus I2C correspondiente al canal actual del multiplexor y lo almacena en el diccionario de sensores
            print(f"Canal {canal}: sensor OK")#imprime un mensaje indicando que el sensor se ha inicializado correctamente en el canal actual del multiplexor

        except Exception as error:#si ocurre un error al intentar inicializar un sensor en el canal actual del multiplexor, se captura la excepción y se imprime un mensaje indicando que hubo un error al iniciar el sensor en ese canal
            print(f"Canal {canal}: error al iniciar: {error}")

    return sensores#devuelve el diccionario de sensores inicializados en los ocho canales del multiplexor, donde cada clave es el número de canal y cada valor es el objeto del sensor correspondiente


def leer_distancia(sensor):#define la función que devuelve la distancia medida por un sensor en milímetros
    """Devuelve la distancia medida en milímetros."""
    try:
        return sensor.range#devuelve la distancia medida por el sensor en milímetros
    except Exception as error:#si ocurre un error al intentar leer la distancia del sensor, se captura la excepción y se imprime un mensaje indicando que hubo un error al leer el sensor, y se devuelve None para indicar que no se pudo obtener una lectura válida
        print(f"Error leyendo sensor: {error}")
        return None#retorna None para indicar que no se pudo obtener una lectura válida del sensor


def leer_todos(sensores):#define la función que devuelve un diccionario con las distancias actuales medidas por todos los sensores disponibles en los ocho canales del multiplexor
    """Devuelve un diccionario con las distancias actuales."""
    distancias = {}#inicializa un diccionario vacío para almacenar las distancias medidas por todos los sensores disponibles en los ocho canales del multiplexor

    for canal, sensor in sensores.items():#itera sobre los elementos del diccionario de sensores, donde cada clave es el número de canal y cada valor es el objeto del sensor correspondiente, para leer la distancia medida por cada sensor y almacenarla en el diccionario de distancias
        distancias[canal] = leer_distancia(sensor)#lee la distancia medida por el sensor correspondiente al canal actual y la almacena en el diccionario de distancias, donde la clave es el número de canal y el valor es la distancia medida en milímetros (o None si no se pudo obtener una lectura válida)

    return distancias#devuelve el diccionario de distancias medidas por todos los sensores disponibles en los ocho canales del multiplexor, donde cada clave es el número de canal y cada valor es la distancia medida en milímetros (o None si no se pudo obtener una lectura válida)


def mostrar_distancias(distancias):#define la función que imprime en la consola las distancias medidas por todos los sensores disponibles en los ocho canales del multiplexor, indicando si no se pudo obtener una lectura válida para algún sensor
    """Muestra las distancias disponibles."""
    for canal, distancia in distancias.items():#itera sobre los elementos del diccionario de distancias, donde cada clave es el número de canal y cada valor es la distancia medida en milímetros (o None si no se pudo obtener una lectura válida), para imprimir en la consola las distancias medidas por todos los sensores disponibles en los ocho canales del multiplexor
        if distancia is None:#si la distancia medida por el sensor correspondiente al canal actual es None (es decir, no se pudo obtener una lectura válida), se imprime un mensaje indicando que no se pudo obtener una lectura para ese canal
            print(f"Canal {canal}: sin lectura")
        else:#si la distancia medida por el sensor correspondiente al canal actual es un valor válido (es decir, no es None), se imprime un mensaje indicando la distancia medida en milímetros para ese canal
            print(f"Canal {canal}: {distancia} mm")

#formato de impresion
#Canal 0: 123 mm
#Canal 1: sin lectura
#Canal 2: 456 mm
#Canal 3: 789 mm
#Canal 4: 101 mm
#Canal 5: sin lectura
#Canal 6: 112 mm
#Canal 7: 131 mm
