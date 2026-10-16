
import threading

import numpy as np
import sounddevice as sd


# Configuración de audio
FRECUENCIA_MUESTREO = 44100
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
sonidos_activos = {}
fases = {canal: 0.0 for canal in FRECUENCIAS}
bloqueo = threading.Lock()
flujo_audio = None





def generar_audio(outdata, frames, time_info, status):
    """Genera audio estéreo con carga de procesamiento reducida."""

    audio = np.zeros((frames, 2), dtype=np.float32)

    with bloqueo:
        activos = [
            canal for canal in FRECUENCIAS
            if sonidos_activos.get(canal, False)
        ]

    cantidad = len(activos)

    if cantidad == 0:
        outdata[:] = audio
        return

    # Normalizar para evitar que el volumen se dispare
    volumen_canal = VOLUMEN / np.sqrt(len(FRECUENCIAS))

    # Usar precisión simple para reducir trabajo en la Pi Zero
    indices = np.arange(frames, dtype=np.float32)

    for canal in activos:
        frecuencia = FRECUENCIAS[canal]
        incremento = np.float32(
            2.0 * np.pi * frecuencia / FRECUENCIA_MUESTREO
        )

        onda = np.sin(
            np.float32(fases[canal]) + incremento * indices
        )

        fases[canal] = float(
            (fases[canal] + float(incremento) * frames)
            % (2.0 * np.pi)
        )

        pan = PANORAMA[canal]
        izquierda = np.sqrt((1.0 - pan) / 2.0)
        derecha = np.sqrt((1.0 + pan) / 2.0)

        audio[:, 0] += onda * np.float32(volumen_canal * izquierda)
        audio[:, 1] += onda * np.float32(volumen_canal * derecha)

    np.clip(audio, -1.0, 1.0, out=audio)
    outdata[:] = audio





def iniciar_audio():
    """Inicia el flujo continuo de audio."""
    global flujo_audio

    if flujo_audio is not None:
        return

    with bloqueo:
        for canal in FRECUENCIAS:
            sonidos_activos[canal] = False

    flujo_audio = sd.OutputStream(
        samplerate=FRECUENCIA_MUESTREO,
        channels=2,
        dtype="float32",
        blocksize=2048,
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
