
import threading#permite realizar varias tareas al mismo tiempo, como reproducir audio mientras se reciben datos de sensores
import time#permite realizar pausas en la ejecución del programa y medir el tiempo transcurrido
import numpy as np#permite realizar operaciones matemáticas y trabajar con arreglos multidimensionales de manera eficiente
import sounddevice as sd#se utiliza para reproducir audio en tiempo real

# Configuración de audio
FRECUENCIA_MUESTREO = 48000#frecuencia de muestreo del audio en Hz
VOLUMEN = 0.20#volumen del audio (de 0.0 a 1.0)

# Frecuencias asignadas a los ocho canales
FRECUENCIAS = {
    # Sensores delanteros
    0: 130.81,  # Do
    1: 164.81,  # Mi
    2: 196.00,  # Sol
    3: 246.94,  # Si 3ta octaba
    # Sensores traseros
    4: 523.25,  # Do
    5: 659.26,  # Mi
    6: 783.99,  # Sol
    7: 987.77,  # Si 5ta octaba
}


# Posición estéreo: -1 izquierda, +1 derecha
#representa la posición de cada canal de audio en el espacio estéreo, donde -1 indica que el sonido se reproduce completamente en el canal izquierdo, +1 indica que se reproduce completamente en el canal derecho y 0 indica que se reproduce en ambos canales de manera equilibrada
PANORAMA = {
    0: -1.0,
    1: -0.3,
    2:  0.3,
    3:  1.0,
    4: -1.0,
    5: -0.3,
    6:  0.3,
    7:  1.0,
}

# Estado interno
sonidos_activos = {canal: False for canal in FRECUENCIAS}#almacena el estado de cada canal (activo o inactivo)
bloqueo = threading.Lock()#permite sincronizar el acceso a los recursos compartidos entre varios hilos de ejecución, evitando conflictos y garantizando la consistencia de los datos
flujo_audio = None#almacena el objeto de flujo de audio que se utiliza para reproducir el sonido en tiempo real, y se inicializa como None hasta que se crea un flujo de audio válido mediante la función iniciar_audio()


"""crea una tabla de onda sinusoidal para una frecuencia específica,
    que se utilizará para generar el sonido correspondiente a esa frecuencia.
    La función toma como entrada la frecuencia deseada y devuelve un arreglo
    de valores de punto flotante que representan la forma de onda sinusoidal
    para esa frecuencia."""
def _crear_tabla(frecuencia):
    """Crea un bucle con un número entero de ciclos (sin clics al repetir)."""
    ciclos = max(1, int(round(frecuencia)))          # ~1 s de audio
    n = int(round(ciclos * FRECUENCIA_MUESTREO / frecuencia))# longitud del vector
    t = np.arange(n, dtype=np.float64) / FRECUENCIA_MUESTREO# vector de tiempos
    # Se ajusta la frecuencia exacta para que el bucle cierre perfecto
    f_exacta = ciclos * FRECUENCIA_MUESTREO / n# frecuencia exacta
    return np.sin(2 * np.pi * f_exacta * t).astype(np.float32)#retorna la tabla de onda sinusoidal como un arreglo de valores de punto flotante de 32 bits

# Pre-cálculo: tablas de onda y ganancias estéreo (una sola vez)
VOLUMEN_CANAL = VOLUMEN / np.sqrt(len(FRECUENCIAS))#determina el volumen de cada canal individual, dividiendo el volumen total por la raíz cuadrada del número de canales, para mantener un nivel de volumen equilibrado cuando se reproducen múltiples canales simultáneamente

TABLAS_IZQ, TABLAS_DER, LARGO = {}, {}, {}#almacena las tablas de onda para el canal izquierdo y derecho, así como la longitud de cada tabla de onda para cada canal
for c, f in FRECUENCIAS.items():#para cada canal y su frecuencia correspondiente, se crea la tabla de onda sinusoidal y se calcula la ganancia estéreo para el canal izquierdo y derecho, almacenando los resultados en los diccionarios TABLAS_IZQ, TABLAS_DER y LARGO
    base = _crear_tabla(f)#crea la tabla de onda sinusoidal para la frecuencia dada
    pan = PANORAMA[c]#se obtiene la posición estéreo del canal correspondiente
    izq = (base * VOLUMEN_CANAL * np.sqrt((1.0 - pan) / 2.0)).astype(np.float32)#se calcula la ganancia estéreo para el canal izquierdo, multiplicando la tabla de onda por el volumen del canal y ajustando la ganancia según la posición estéreo
    der = (base * VOLUMEN_CANAL * np.sqrt((1.0 + pan) / 2.0)).astype(np.float32)#se calcula la ganancia estéreo para el canal derecho, multiplicando la tabla de onda por el volumen del canal y ajustando la ganancia según la posición estéreo
    TABLAS_IZQ[c] = np.concatenate([izq, izq])#se concatenan las tablas de onda para el canal izquierdo, duplicando la longitud de la tabla para permitir un bucle continuo sin clics al repetir
    TABLAS_DER[c] = np.concatenate([der, der])#se concatenan las tablas de onda para el canal derecho, duplicando la longitud de la tabla para permitir un bucle continuo sin clics al repetir
    LARGO[c] = len(base)#almacena la longitud de la tabla de onda original para cada canal, que se utilizará posteriormente para determinar cuándo reiniciar la reproducción de la tabla de onda al llegar al final

POSICION = {c: 0 for c in FRECUENCIAS}#almacena la posición actual de reproducción de cada canal, inicializando todas las posiciones en cero al inicio del programa. Esta posición se actualizará a medida que se reproduzca el audio, permitiendo que cada canal continúe desde donde se quedó en la siguiente iteración de reproducción.


def generar_audio(outdata, frames, time_info, status):#se encarga de generar el audio en tiempo real, llenando el búfer de salida con los datos de audio correspondientes a los canales activos. Esta función se llama automáticamente por la biblioteca sounddevice cada vez que se necesita generar un nuevo bloque de audio.
    outdata.fill(0)#inicializa el búfer de salida con ceros, asegurando que no haya ruido residual de bloques de audio anteriores

    with bloqueo:#se utiliza un bloqueo para garantizar que el acceso a los recursos compartidos (como la lista de canales activos y las posiciones de reproducción) sea seguro y no se produzcan conflictos entre hilos de ejecución. Esto evita problemas de sincronización y garantiza que los datos se actualicen correctamente mientras se genera el audio.
        activos = [c for c in FRECUENCIAS if sonidos_activos[c]]#se crea una lista de canales activos, es decir, aquellos canales que están actualmente activados para reproducir sonido. Esto se hace filtrando los canales en FRECUENCIAS y verificando si su estado en sonidos_activos es True.

    for canal in activos:#se itera sobre cada canal activo y se genera el audio correspondiente para ese canal. Se obtiene la posición actual de reproducción del canal, se agregan los datos de audio a los canales izquierdo y derecho del búfer de salida, y se actualiza la posición de reproducción para el siguiente bloque de audio.
        pos = POSICION[canal]#se obtiene la posición actual de reproducción del canal
        outdata[:, 0] += TABLAS_IZQ[canal][pos:pos + frames]#se agregan los datos de audio correspondientes al canal izquierdo del búfer de salida, utilizando la tabla de onda para el canal izquierdo y tomando los valores desde la posición actual hasta la posición actual más el número de frames a generar
        outdata[:, 1] += TABLAS_DER[canal][pos:pos + frames]#se agregan los datos de audio correspondientes al canal derecho del búfer de salida, utilizando la tabla de onda para el canal derecho y tomando los valores desde la posición actual hasta la posición actual más el número de frames a generar
        POSICION[canal] = (pos + frames) % LARGO[canal]#se actualiza la posición de reproducción del canal, sumando el número de frames generados y utilizando el operador módulo para asegurarse de que la posición se mantenga dentro del rango válido de la tabla de onda. Esto permite que la reproducción del canal continúe desde el principio de la tabla de onda una vez que se alcanza el final.

    np.clip(outdata, -1.0, 1.0, out=outdata)#se asegura de que los valores de audio en el búfer de salida estén dentro del rango válido de -1.0 a 1.0, evitando distorsiones o recortes en el audio generado. La función np.clip toma el búfer de salida y limita sus valores a este rango, sobrescribiendo los valores fuera del rango con los límites correspondientes.



"""
inicia el flujo de audio para la reproducción en tiempo real.
Si el flujo de audio ya está activo, no realiza ninguna acción adicional.
De lo contrario, crea un nuevo flujo de salida utilizando la biblioteca sounddevice,
configurando la frecuencia de muestreo, el número de canales, el tipo de datos,
el tamaño del bloque y la latencia. Además, se establece la función generar_audio
como callback para generar los datos de audio en tiempo real.
Finalmente, se inicia el flujo de audio y se imprime un mensaje indicando
que el audio se ha iniciado correctamente.
"""
def iniciar_audio():
    global flujo_audio#se utiliza la palabra clave global para indicar que se está accediendo a la variable flujo_audio definida en el ámbito global, lo que permite modificar su valor dentro de la función iniciar_audio.
    if flujo_audio is not None:#si el flujo de audio ya está activo (es decir, no es None), significa que el audio ya se ha iniciado previamente, por lo que no es necesario realizar ninguna acción adicional y se retorna inmediatamente de la función.
        return

    flujo_audio = sd.OutputStream(#se crea un flujo de salida de audio utilizando la biblioteca sounddevice, que permite reproducir audio en tiempo real. Se configuran varios parámetros para el flujo de salida, como la frecuencia de muestreo, el número de canales, el tipo de datos, el tamaño del bloque y la latencia. Además, se establece la función generar_audio como callback para generar los datos de audio en tiempo real.
        samplerate=FRECUENCIA_MUESTREO,#se establece la frecuencia de muestreo del flujo de audio, que determina cuántas muestras de audio se capturan por segundo. En este caso, se utiliza la constante FRECUENCIA_MUESTREO definida previamente.
        channels=2,#se establece el número de canales de audio del flujo de salida. En este caso, se utiliza 2 canales, lo que indica que se reproducirá audio estéreo (canal izquierdo y canal derecho).
        dtype="float32",#se establece el tipo de datos utilizado para representar las muestras de audio en el flujo de salida. En este caso, se utiliza "float32", lo que significa que cada muestra de audio se representará como un número de punto flotante de 32 bits.
        blocksize=4096,      # bloque más grande = menos llamadas por segundo, se reduce la carga de la CPU y el riesgo de interrupciones
        latency="high",      # búfer holgado, ideal para Bluetooth, ayuda a evitar cortes de audio y proporciona una reproducción más estable, especialmente en entornos donde la latencia puede ser un problema, como al utilizar dispositivos Bluetooth.
        callback=generar_audio,#se establece la función generar_audio como callback para el flujo de salida. Esto significa que cada vez que se necesiten nuevos datos de audio para reproducir, la función generar_audio se llamará automáticamente para llenar el búfer de salida con los datos de audio correspondientes a los canales activos.
    )
    flujo_audio.start()#inicia el flujo de salida de audio, lo que permite que comience la reproducción en tiempo real. Una vez que se llama a este método, el flujo de audio comenzará a generar y reproducir los datos de audio según la configuración establecida anteriormente.
    print("Audio iniciado correctamente.")


def actualizar_audio(distancias, umbral_mm=1000):#se encarga de actualizar el estado de los canales de audio en función de las distancias medidas por los sensores. Toma como entrada un diccionario distancias que contiene las distancias medidas para cada canal y un umbral umbral_mm que determina la distancia máxima para activar un canal. La función recorre cada canal y verifica si la distancia medida está dentro del rango permitido (mayor que cero y menor o igual al umbral). Si es así, activa el canal correspondiente en sonidos_activos; de lo contrario, lo desactiva. Se utiliza un bloqueo para garantizar que el acceso a sonidos_activos sea seguro y no se produzcan conflictos entre hilos de ejecución.
    """Activa las notas de los sensores dentro del umbral."""
    with bloqueo:#se utiliza un bloqueo para garantizar que el acceso a sonidos_activos sea seguro y no se produzcan conflictos entre hilos de ejecución. Esto evita problemas de sincronización y garantiza que los datos se actualicen correctamente mientras se actualiza el estado de los canales de audio.
        for canal in FRECUENCIAS:  #se itera sobre cada canal definido en FRECUENCIAS, que representa los canales de audio correspondientes a los sensores. Para cada canal, se obtiene la distancia medida desde el diccionario distancias y se verifica si está dentro del rango permitido (mayor que cero y menor o igual al umbral). Si es así, se activa el canal correspondiente en sonidos_activos; de lo contrario, se desactiva.
            distancia = distancias.get(canal)#se obtiene la distancia medida para el canal actual desde el diccionario distancias utilizando el método get(). Si no se encuentra una distancia para ese canal, se asigna None como valor predeterminado.

            sonidos_activos[canal] = (#se actualiza el estado del canal en sonidos_activos, estableciendo su valor en True si la distancia medida está dentro del rango permitido (mayor que cero y menor o igual al umbral), o en False si no lo está. Esto determina si el canal estará activo o inactivo para la reproducción de audio.
                distancia is not None
                and 0 < distancia <= umbral_mm
            )


def detener_audio():#se encarga de silenciar todos los canales de audio. Toma como entrada un diccionario distancias que contiene las distancias medidas para cada canal y un umbral umbral_mm que determina la distancia máxima para activar un canal. La función recorre cada canal y verifica si la distancia medida está dentro del rango permitido (mayor que cero y menor o igual al umbral). Si es así, activa el canal correspondiente en sonidos_activos; de lo contrario, lo desactiva. Se utiliza un bloqueo para garantizar que el acceso a sonidos_activos sea seguro y no se produzcan conflictos entre hilos de ejecución.
    """Silencia todos los canales."""
    with bloqueo:
        for canal in FRECUENCIAS:#se itera sobre cada canal definido en FRECUENCIAS y se establece su estado en sonidos_activos como False, lo que indica que todos los canales estarán inactivos y no se reproducirá ningún sonido.
            sonidos_activos[canal] = False#se actualiza el estado del canal en sonidos_activos, estableciendo su valor en False para silenciar el canal y evitar que se reproduzca sonido.


def cerrar_audio():#se encarga de detener y cerrar el flujo de audio. Primero, llama a la función detener_audio() para silenciar todos los canales. Luego, verifica si el flujo de audio está activo (es decir, si flujo_audio no es None). Si está activo, detiene el flujo de audio utilizando el método stop(), cierra el flujo utilizando el método close() y establece flujo_audio en None para indicar que ya no hay un flujo de audio activo. Finalmente, imprime un mensaje indicando que el audio se ha cerrado correctamente.
    """Detiene y cierra el flujo de audio."""
    global flujo_audio#se utiliza la palabra clave global para indicar que se está accediendo a la variable flujo_audio definida en el ámbito global, lo que permite modificar su valor dentro de la función cerrar_audio.

    detener_audio()#se llama a la función detener_audio() para silenciar todos los canales de audio antes de cerrar el flujo de audio. Esto garantiza que no haya sonido activo mientras se cierra el flujo.

    if flujo_audio is not None:#se verifica si el flujo de audio está activo (es decir, si flujo_audio no es None). Si está activo, se procede a detener y cerrar el flujo de audio.
        flujo_audio.stop()#se detiene el flujo de audio utilizando el método stop(), lo que detiene la reproducción de audio en tiempo real y libera los recursos asociados al flujo.
        flujo_audio.close()#se cierra el flujo de audio utilizando el método close(), lo que libera los recursos asociados al flujo y finaliza la reproducción de audio en tiempo real.
        flujo_audio = None#se establece flujo_audio en None para indicar que ya no hay un flujo de audio activo. Esto permite que la función iniciar_audio() pueda crear un nuevo flujo de audio en el futuro si es necesario.

    print("Audio cerrado.")



"""___________________________________________________________"""


def probar_audio(duracion=2):
    """Prueba cada canal y varias notas simultáneas."""
    iniciar_audio()

    try:
        for canal in FRECUENCIAS:
            print(f"Probando canal {canal}")

            distancias = {
                numero: None for numero in FRECUENCIAS
            }
            distancias[canal] = 500

            actualizar_audio(distancias, umbral_mm=1000)
            time.sleep(duracion)

        for cantidad in (1, 2, 3, 4, 8):
            print(f"\nProbando {cantidad} notas simultáneas...")

            distancias = {
                canal: (500 if canal < cantidad else None)
                for canal in FRECUENCIAS
            }

            actualizar_audio(distancias, umbral_mm=1000)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nPrueba interrumpida.")

    finally:
        cerrar_audio()

if __name__ == "__main__":
    probar_audio()
