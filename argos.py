import os
from pathlib import Path


CARPETA_ARGOS = Path.home() / "Argos"
PYTHON_VENV = CARPETA_ARGOS / "venv" / "bin" / "python"
PROGRAMA_ARGOS = CARPETA_ARGOS / "main.py"


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
        print("1. Iniciar")
        print("2. Cerrar")

        try:
            opcion = input("Elige una opción (1/2): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nMenú cerrado.")
            return

        if opcion == "1":
            try:
                iniciar_argos()
            except OSError as error:
                print(f"No se pudo iniciar ARGOS: {error}")
        elif opcion == "2":
            print("Menú cerrado.")
            return
        else:
            print("Opción no válida. Escribe 1 o 2.")


if __name__ == "__main__":
    main()
