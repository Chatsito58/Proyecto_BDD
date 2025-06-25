import sqlite3
from sqlite3 import Connection, Error
from utils.logger import logger


def conectar_db(db_path: str | None = None) -> Connection | None:
    """Return a SQLite connection or None if there is an error."""
    try:
        path = db_path or ":memory:"
        conn = sqlite3.connect(path)
        return conn
    except Error as exc:
        logger.error(f"Error al conectar a la base de datos: {exc}")
        return None


def cerrar_db(conn: Connection | None) -> None:
    """Close the given connection handling any error."""
    if not conn:
        return
    try:
        conn.close()
    except Error as exc:
        logger.error(f"Error al cerrar la conexión: {exc}")
