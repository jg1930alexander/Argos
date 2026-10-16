
import subprocess
import time


def audifonos_conectados():
    """Comprueba que los KVIDIO 201 estén conectados y sean la salida activa."""

    try:
        bluetooth = subprocess.run(
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        pipewire = subprocess.run(
            ["wpctl", "status"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        if bluetooth.returncode != 0 or pipewire.returncode != 0:
            return False

        conectados = bluetooth.stdout.lower()
        audio = pipewire.stdout.lower()

        return (
            "kvidio 201" in conectados
            and "kvidio 201" in audio
            and "sinks:" in audio
        )

    except (subprocess.TimeoutExpired, OSError):
        return False


def esperar_audifonos(intervalo=2):
    """Espera indefinidamente hasta que estén conectados."""

    while not audifonos_conectados():
        print("Esperando conexión de los audífonos KVIDIO 201...")
        time.sleep(intervalo)

    print("Audífonos KVIDIO 201 conectados.")
