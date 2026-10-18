import signal
import subprocess
from pathlib import Path


CARPETA_ARGOS = Path.home() / "Argos"
PYTHON_VENV = CARPETA_ARGOS / "venv" / "bin" / "python"
PROGRAMA_ARGOS = CARPETA_ARGOS / "main.py"
ARCHIVO_LOG = CARPETA_ARGOS / "argos.log"


def iniciar_argos():
    if not PYTHON_VENV.is_file():
        print(f"No encuentro el intérprete del entorno virtual: {PYTHON_VENV}")
        return None, None

    if not PROGRAMA_ARGOS.is_file():
        print(f"No encuentro el programa: {PROGRAMA_ARGOS}")
        return None, None

    archivo_log = ARCHIVO_LOG.open("a", encoding="utf-8")
    archivo_log.write("\n--- Iniciando ARGOS ---\n")
    archivo_log.flush()

    try:
        proceso = subprocess.Popen(
            [str(PYTHON_VENV), "-u", str(PROGRAMA_ARGOS)],
            cwd=CARPETA_ARGOS,
            stdin=subprocess.DEVNULL,
            stdout=archivo_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError as error:
        archivo_log.close()
        print(f"No se pudo iniciar ARGOS: {error}")
        return None, None

    print(f"ARGOS iniciado (PID {proceso.pid}).")
    print(f"Salida del programa: {ARCHIVO_LOG}")
    return proceso, archivo_log


def cerrar_argos(proceso, archivo_log):
    if proceso is None:
        print("ARGOS no está en ejecución.")
        return None, None

    if proceso.poll() is not None:
        print(f"ARGOS ya había terminado (código {proceso.returncode}).")
    else:
        print("Solicitando cierre de ARGOS...")
        try:
            proceso.send_signal(signal.SIGINT)
            proceso.wait(timeout=8)
        except subprocess.TimeoutExpired:
            print("ARGOS no respondió; se intentará detenerlo.")
            proceso.terminate()
            try:
                proceso.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print("ARGOS sigue activo; se finalizará el proceso.")
                proceso.kill()
                proceso.wait()
        except OSError as error:
            print(f"No se pudo solicitar el cierre normal: {error}")
            proceso.terminate()
            proceso.wait()

        print("ARGOS cerrado.")

    if archivo_log is not None:
        archivo_log.close()
    return None, None


def main():
    proceso = None
    archivo_log = None

    try:
        while True:
            if proceso is not None and proceso.poll() is not None:
                print(f"ARGOS terminó (código {proceso.returncode}).")
                if archivo_log is not None:
                    archivo_log.close()
                proceso = None
                archivo_log = None

            print("\n=== Menú ARGOS ===")
            print("1. Iniciar")
            print("2. Cerrar")

            opcion = input("Elige una opción (1/2): ").strip()

            if opcion == "1":
                if proceso is not None:
                    print("ARGOS ya está en ejecución.")
                else:
                    proceso, archivo_log = iniciar_argos()
            elif opcion == "2":
                proceso, archivo_log = cerrar_argos(proceso, archivo_log)
                print("Menú cerrado.")
                break
            else:
                print("Opción no válida. Escribe 1 o 2.")

    except (KeyboardInterrupt, EOFError):
        print("\nCerrando el menú.")
    finally:
        if proceso is not None:
            cerrar_argos(proceso, archivo_log)


if __name__ == "__main__":
    main()
