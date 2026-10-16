
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
ganancias_actuales = {canal: 0.0 for canal in FRECUENCIAS}
bloqueo = threading.Lock()
flujo_audio = None




def generar_audio(outdata, frames, time_info, status):
    """Mezcla las ocho notas con transiciones suaves."""
    audio = np.zeros((frames, 2), dtype=np.float32)

    with bloqueo:
        activos = sonidos_activos.copy()

    indices = np.arange(frames, dtype=np.float64)
    muestras_rampa = max(1, int(0.010 * FRECUENCIA_MUESTREO))

    # Volumen fijo por canal para evitar saltos al sumar notas
    volumen_canal = VOLUMEN / np.sqrt(len(FRECUENCIAS))

    for canal, frecuencia in FRECUENCIAS.items():
        ganancia_inicial = ganancias_actuales[canal]
        ganancia_objetivo = 1.0 if activos.get(canal, False) else 0.0

        # Suavizar el cambio de volumen
        longitud = min(frames, muestras_rampa)

        rampa = np.linspace(
            ganancia_inicial,
            ganancia_objetivo,
            longitud,
            endpoint=True
        )

        ganancias = np.full(frames, ganancia_objetivo, dtype=np.float64)
        ganancias[:longitud] = rampa

        ganancias_actuales[canal] = ganancia_objetivo

        # Si está completamente silenciado, no hace falta generar su onda
        if ganancia_objetivo == 0.0 and ganancia_inicial == 0.0:
            continue

        incremento = 2 * np.pi * frecuencia / FRECUENCIA_MUESTREO

        onda = np.sin(
            fases[canal] + incremento * indices
        )

        fases[canal] = (
            fases[canal] + incremento * frames
        ) % (2 * np.pi)

        pan = PANORAMA[canal]
        ganancia_izquierda = np.sqrt((1 - pan) / 2)
        ganancia_derecha = np.sqrt((1 + pan) / 2)

        senal = onda * ganancias * volumen_canal

        audio[:, 0] += senal * ganancia_izquierda
        audio[:, 1] += senal * ganancia_derecha

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
