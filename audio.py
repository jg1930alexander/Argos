
import threading
import time
import numpy as np
import sounddevice as sd

# Configuración de audio
FRECUENCIA_MUESTREO = 48000
VOLUMEN = 0.20

# Frecuencias asignadas a los ocho canales
FRECUENCIAS = {
    # Sensores delanteros
    0: 261.63,  # Do
    1: 329.63,  # Mi
    2: 392.00,  # Sol
    3: 493.88,  # Si

    # Sensores traseros
    4: 220.00,  # La grave
    5: 293.66,  # Re
    6: 349.23,  # Fa
    7: 440.00,  # La
}


# Posición estéreo: -1 izquierda, +1 derecha
PANORAMA = {
    0: -1.0,
    1: -0.5,
    2:  0.5,
    3:  1.0,
    4: -1.0,
    5: -0.5,
    6:  0.5,
    7:  1.0,
}

# Estado interno
sonidos_activos = {canal: False for canal in FRECUENCIAS}
bloqueo = threading.Lock()
flujo_audio = None


def _crear_tabla(frecuencia):
    """Crea un bucle con un número entero de ciclos (sin clics al repetir)."""
    ciclos = max(1, int(round(frecuencia)))          # ~1 s de audio
    n = int(round(ciclos * FRECUENCIA_MUESTREO / frecuencia))
    t = np.arange(n, dtype=np.float64) / FRECUENCIA_MUESTREO
    # Se ajusta la frecuencia exacta para que el bucle cierre perfecto
    f_exacta = ciclos * FRECUENCIA_MUESTREO / n
    return np.sin(2 * np.pi * f_exacta * t).astype(np.float32)

# Pre-cálculo: tablas de onda y ganancias estéreo (una sola vez)
VOLUMEN_CANAL = VOLUMEN / np.sqrt(len(FRECUENCIAS))

TABLAS_IZQ, TABLAS_DER, LARGO = {}, {}, {}
for c, f in FRECUENCIAS.items():
    base = _crear_tabla(f)
    pan = PANORAMA[c]
    izq = (base * VOLUMEN_CANAL * np.sqrt((1.0 - pan) / 2.0)).astype(np.float32)
    der = (base * VOLUMEN_CANAL * np.sqrt((1.0 + pan) / 2.0)).astype(np.float32)
    TABLAS_IZQ[c] = np.concatenate([izq, izq])   # duplicada
    TABLAS_DER[c] = np.concatenate([der, der])
    LARGO[c] = len(base)

POSICION = {c: 0 for c in FRECUENCIAS}



def generar_audio(outdata, frames, time_info, status):
    outdata.fill(0)

    with bloqueo:
        activos = [c for c in FRECUENCIAS if sonidos_activos[c]]

    for canal in activos:
        pos = POSICION[canal]
        outdata[:, 0] += TABLAS_IZQ[canal][pos:pos + frames]
        outdata[:, 1] += TABLAS_DER[canal][pos:pos + frames]
        POSICION[canal] = (pos + frames) % LARGO[canal]

    np.clip(outdata, -1.0, 1.0, out=outdata)





def iniciar_audio():
    global flujo_audio
    if flujo_audio is not None:
        return

    #Espera que el dispositivo Bluetooth esté disponible antes de iniciar el flujo de audio
    #indice_bt = None

    flujo_audio = sd.OutputStream(
        samplerate=FRECUENCIA_MUESTREO,
        channels=2,
        dtype="float32",
        blocksize=4096,      # bloque más grande = menos llamadas por segundo
        latency="high",      # búfer holgado, ideal para Bluetooth
        callback=generar_audio,
    )
    flujo_audio.start()
    print("Audio iniciado correctamente.")


def actualizar_audio(distancias, umbral_mm=1000):
    """Activa las notas de los sensores dentro del umbral."""
    with bloqueo:
        for canal in FRECUENCIAS:
            distancia = distancias.get(canal)

            sonidos_activos[canal] = (
                distancia is not None
                and 0 < distancia <= umbral_mm
            )


def detener_audio():
    """Silencia todos los canales."""
    with bloqueo:
        for canal in FRECUENCIAS:
            sonidos_activos[canal] = False


def cerrar_audio():
    """Detiene y cierra el flujo de audio."""
    global flujo_audio

    detener_audio()

    if flujo_audio is not None:
        flujo_audio.stop()
        flujo_audio.close()
        flujo_audio = None

    print("Audio cerrado.")



"""___________________________________________________________"""
import time


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
