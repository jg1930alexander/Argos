import os
import subprocess
from pathlib import Path


CARPETA_ARGOS = Path.home() / "Argos"
PYTHON_VENV = CARPETA_ARGOS / "venv" / "bin" / "python"
PROGRAMA_ARGOS = CARPETA_ARGOS / "main.py"
SERVICIO_ARGOS = "argos.service"


def mostrar_estado_arranque():
    try:
        resultado = subprocess.run(
            ["systemctl", "is-enabled", SERVICIO_ARGOS],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        print(f"No se pudo consultar el estado de {SERVICIO_ARGOS}: {error}")
        return

    estado = (resultado.stdout or resultado.stderr).strip()
    if estado == "enabled":
        print("Arranque automático: activado.")
    elif estado == "disabled":
        print("Arranque automático: desactivado.")
    elif estado == "enabled-runtime":
        print("Arranque automático: activado solo temporalmente.")
    else:
        detalle = estado or f"código {resultado.returncode}"
        print(f"Estado de arranque de {SERVICIO_ARGOS}: {detalle}.")


def cambiar_arranque(accion):
    try:
        resultado = subprocess.run(
            ["sudo", "systemctl", accion, SERVICIO_ARGOS],
            check=False,
        )
    except OSError as error:
        print(f"No se pudo ejecutar systemctl {accion}: {error}")
        return

    if resultado.returncode != 0:
        print(
            f"No se pudo {accion} el arranque automático "
            f"(código {resultado.returncode})."
        )


def mostrar_logs():
    try:
        subprocess.run(
            ["sudo", "journalctl", "-u", SERVICIO_ARGOS, "-f"],
            check=False,
        )
    except OSError as error:
        print(f"No se pudieron mostrar los logs de {SERVICIO_ARGOS}: {error}")
    except KeyboardInterrupt:
        print("\nSe detuvo la consulta de logs.")


def iniciar_argos():
    if not PYTHON_VENV.is_file():
        raise FileNotFoundError(
            f"No encuentro el intérprete del entorno virtual: {PYTHON_VENV}"
        )

    if not PROGRAMA_ARGOS.is_file():
        raise FileNotFoundError(f"No encuentro el programa: {PROGRAMA_ARGOS}")

    os.chdir(CARPETA_ARGOS)
    os.execv(
        str(PYTHON_VENV),
        [str(PYTHON_VENV), "-u", str(PROGRAMA_ARGOS)],
    )


def main():
    while True:
        print("\n=== Menú ARGOS ===")
        mostrar_estado_arranque()
        print("1. Iniciar")
        print("2. Activar arranque con el sistema")
        print("3. Desactivar arranque con el sistema")
        print("4. Mostrar logs del servicio")
        print("5. Cerrar")

        try:
            opcion = input("Elige una opción (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nMenú cerrado.")
            return

        if opcion == "1":
            try:
                iniciar_argos()
            except OSError as error:
                print(f"No se pudo iniciar ARGOS: {error}")
        elif opcion == "2":
            cambiar_arranque("enable")
        elif opcion == "3":
            cambiar_arranque("disable")
        elif opcion == "4":
            mostrar_logs()
        elif opcion == "5":
            print("Menú cerrado.")
            return
        else:
            print("Opción no válida. Escribe un número del 1 al 5.")


if __name__ == "__main__":
    main()
