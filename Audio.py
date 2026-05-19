import numpy as np
import sounddevice as sd
from pynput import keyboard

sample_rate = 44100
volumen = 0.4

# Frecuencias de las notas
notas = {
    
    'a': 261.63,  # Do
    's': 329.63,  # Mi
    'd': 392.00,  # Sol
    'f': 493.88,  # Si

    'z': 261.63,  # Do
    'x': 329.63,  # Mi
    'c': 392.00,  # Sol
    'v': 493.88  # Si

}

# Paneo estéreo
# -1 = izquierda
#  0 = centro
#  1 = derecha
paneo = {
    
    'a': -1.0,
    's': -0.5,
    'd': 0.5,
    'f': 1.0,

    'z': -1.0,
    'x': -0.5,
    'c': 0.5,
    'v': 1.0
}

# Posición espacial
profundidad = {
    
    'a': 'front',
    's': 'front',
    'd': 'front',
    'f': 'front',

    'z': 'back',
    'x': 'back',
    'c': 'back',
    'v': 'back'
}

# Teclas activas
teclas_activas = set()

# Fase global
fase = 0

def audio_callback(outdata, frames, time, status):
    global fase

    # Tiempo
    t = (np.arange(frames) + fase) / sample_rate

    # Canales estéreo
    left = np.zeros(frames)
    right = np.zeros(frames)

    for tecla in teclas_activas:

        frecuencia = notas[tecla]

        # Onda base
        onda = np.sin(2 * np.pi * frecuencia * t)

        # Profundidad espacial
        posicion = profundidad[tecla]

        # SONIDO DETRÁS
        if posicion == 'back':

            # Menos volumen
            onda *= 0.5

            # Menos agudos
            filtro = np.ones(5) / 5

            onda = np.convolve(
                onda,
                filtro,
                mode='same'
            )

            onda = onda[:frames]

            # Pequeño eco/retraso
            delay = min(80, frames - 1)

            onda_delay = np.roll(onda, delay)

            onda = onda + onda_delay * 0.3

        # SONIDO CENTRO
        elif posicion == 'center':
            onda *= 0.8

        # Paneo
        pan = paneo[tecla]

        left_gain = (1 - pan) / 2
        right_gain = (1 + pan) / 2

        left += onda * left_gain
        right += onda * right_gain

    # Normalizar volumen
    if len(teclas_activas) > 0:
        left /= len(teclas_activas)
        right /= len(teclas_activas)

    # Combinar estéreo
    stereo = np.column_stack((left, right))

    # Salida final
    outdata[:] = stereo * volumen

    fase += frames

# Tecla presionada
def on_press(key):
    try:
        tecla = key.char.lower()

        if tecla in notas:
            teclas_activas.add(tecla)

    except:
        pass

# Tecla soltada
def on_release(key):
    try:
        tecla = key.char.lower()

        teclas_activas.discard(tecla)

    except:
        pass

    # Salir con ESC
    if key == keyboard.Key.esc:
        return False

print("Piano espacial activo")
print("A S D F ")
print("Z X C V ")
print("Posicionamiento 8 direcciones")
print("ESC para salir")

# Stream de audio
with sd.OutputStream(
    channels=2,
    callback=audio_callback,
    samplerate=sample_rate
):

    # Escuchar teclado
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:

        listener.join()