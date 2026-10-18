
import subprocess#modulo para ejecutar comandos del sistema operativo desde Python
import time#modulo para trabajar con el tiempo y realizar pausas en la ejecución del programa


def audifonos_conectados():
    """Comprueba que los KVIDIO 201 estén conectados y sean la salida activa."""

    try:#intenta ejecutar los comandos del sistema operativo para comprobar la conexión de los audífonos
        bluetooth = subprocess.run(#entra al comando bluetoothctl para obtener la lista de dispositivos Bluetooth conectados y captura la salida del comando en formato de texto, con un tiempo máximo de espera de 3 segundos
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        pipewire = subprocess.run(#entra al comando wpctl para obtener el estado de PipeWire y captura la salida del comando en formato de texto, con un tiempo máximo de espera de 3 segundos
            ["wpctl", "status"],#mostrar el estado actual y la lista de todos los dispositivos de audio y video administrados por el sistema de sonido moderno de Linux llamado PipeWire
            capture_output=True,
            text=True,
            timeout=3,
        )
        if bluetooth.returncode != 0 or pipewire.returncode != 0:#si alguno de los comandos devuelve un código de error (es decir, no se ejecutó correctamente), se retorna False para indicar que no se pudo comprobar la conexión de los audífonos
            return False

        conectados = bluetooth.stdout.lower()#almacena la salida del comando bluetoothctl en minúsculas para facilitar la búsqueda de la cadena "kvidio 201" que indica que los audífonos están conectados
        audio = pipewire.stdout.lower()#almacena la salida del comando wpctl en minúsculas para facilitar la búsqueda de las cadenas "kvidio 201" y "sinks:" que indican que los audífonos están conectados y son la salida activa de audio

        return (#retorna True si se cumplen las tres condiciones siguientes: los audífonos KVIDIO 201 están conectados, son la salida activa de audio y están listados en la salida del comando wpctl; de lo contrario, retorna False
            "kvidio 201" in conectados
            and "kvidio 201" in audio
            and "sinks:" in audio
        )

    except (subprocess.TimeoutExpired, OSError):#si ocurre un error al ejecutar los comandos del sistema operativo (por ejemplo, si el comando no se encuentra o si tarda demasiado en ejecutarse), se retorna False para indicar que no se pudo comprobar la conexión de los audífonos
        return False


def esperar_audifonos(intervalo=2):
    """Espera indefinidamente hasta que estén conectados."""

    while not audifonos_conectados():#mientras los audífonos KVIDIO 201 no estén conectados, se imprime un mensaje indicando que se está esperando la conexión de los audífonos y se realiza una pausa en la ejecución del programa durante el intervalo de tiempo especificado (por defecto, 2 segundos) antes de volver a comprobar la conexión de los audífonos
        print("Esperando conexión de los audífonos KVIDIO 201...")
        time.sleep(intervalo)

    print("Audífonos KVIDIO 201 conectados.")
