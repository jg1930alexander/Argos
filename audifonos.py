
import sounddevice as sd
import time

def esperar_dispositivo_bluetooth(max_intentos=30, intervalo=1):
    """Espera hasta encontrar la salida Bluetooth de los audífonos."""

    for intento in range(max_intentos):
        dispositivos = sd.query_devices()

        for i, dev in enumerate(dispositivos):
            nombre = dev["name"].lower()

            if (
                dev["max_output_channels"] >= 2
                and ("bluez" in nombre or "kvidio" in nombre)
            ):
                print(
                    f"Salida encontrada: {dev['name']} "
                    f"(índice {i})"
                )
                return i

        print(
            f"Esperando audífonos Bluetooth... "
            f"({intento + 1}/{max_intentos})"
        )
        time.sleep(intervalo)

    raise RuntimeError(
        "No se encontró la salida Bluetooth de los audífonos."
    )
