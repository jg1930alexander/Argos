
import threading

import numpy as np
import sounddevice as sd


# Configuración de audio
FRECUENCIA_MUESTREO = 44100
VOLUMEN = 0.20

# Frecuencias asignadas a los ocho canales
FRECUENCIAS = {
    0: 261.63,  # Do
    1: 329.63,  # Mi
    2: 392.00,  # Sol
    3: 493.88,  # Si
    4: 261.63,  # Do
    5: 329.63,  # Mi
    6: 392.00,  # Sol
    7: 493.88,  # Si
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
    """Genera las notas activas en estéreo."""
    audio = np.zeros((frames, 2), dtype=np.float32)

    with bloqueo:
        activos = list(sonidos_activos.items())

    for canal, activo in activos:
        if not activo:
            continue

        frecuencia = FRECUENCIAS[canal]
        pan = PANORAMA[canal]

        # Generar onda sinusoidal
        fase_inicial = fases[canal]
        incremento = 2 * np.pi * frecuencia / FRECUENCIA_MUESTREO

        indices = np.arange(frames)
        onda = np.sin(fase_inicial + incremento * indices)

        fases[canal] = (
            fase_inicial + incremento * frames
        ) % (2 * np.pi)

        # Distribución estéreo
        ganancia_izquierda = np.sqrt((1 - pan) / 2)
        ganancia_derecha = np.sqrt((1 + pan) / 2)

        audio[:, 0] += (
            onda * ganancia_izquierda * VOLUMEN
        )
        audio[:, 1] += (
            onda * ganancia_derecha * VOLUMEN
        )

    # Evitar saturación al mezclar varias notas
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
        blocksize=512,
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
    """Reproduce una nota de prueba por cada canal."""
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

        detener_audio()

    finally:
        cerrar_audio()


if __name__ == "__main__":
    probar_audio()
