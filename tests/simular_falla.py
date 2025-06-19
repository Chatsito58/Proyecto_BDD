"""Simula la caída de un nodo y verifica el failover."""

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from conexion.conexion import ConexionBD
from utils.logger import configurar_logging


def main() -> None:
    configurar_logging()
    db = ConexionBD()
    try:
        db.ejecutar("SELECT 1")
        logging.info("Conexión inicial operativa en %s", db.active)
        db.active = "remote" if db.active == "local" else "local"
        db.conectar()
        db.ejecutar("SELECT 1")
        logging.info("Failover manual a %s exitoso", db.active)
    except Exception as exc:
        logging.error("Error durante simulación: %s", exc)


if __name__ == "__main__":
    main()
