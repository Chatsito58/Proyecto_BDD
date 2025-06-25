import json
import os
from dotenv import load_dotenv
from mysql.connector import connect, Error
from utils.logger import configurar_logging, logger

load_dotenv()

FEDERADA_CONF = {
    "host": os.getenv("DB_FRAG_HOST"),
    "port": int(os.getenv("DB_FRAG_PORT", 3306)),
    "database": os.getenv("DB_FRAG_NAME"),
    "user": os.getenv("DB_FRAG_USER"),
    "password": os.getenv("DB_FRAG_PASSWORD"),
}

PENDIENTES_PATH = "pendientes_remota.json"


def cargar_pendientes() -> list[dict]:
    """Leer el archivo de pendientes si existe."""
    if not os.path.exists(PENDIENTES_PATH):
        logger.info("No hay archivo de pendientes.")
        return []
    try:
        with open(PENDIENTES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Error leyendo pendientes_remota.json (formato inválido).")
        return []


def guardar_pendientes(pendientes: list[dict]) -> None:
    """Persistir la lista de pendientes en disco."""
    with open(PENDIENTES_PATH, "w", encoding="utf-8") as f:
        json.dump(pendientes, f, indent=2, ensure_ascii=False)


def sincronizar() -> None:
    """Procesar y ejecutar las consultas pendientes."""
    pendientes = cargar_pendientes()
    if not pendientes:
        logger.info("No hay pendientes por procesar.")
        return

    nuevos_pendientes: list[dict] = []

    for item in pendientes:
        query = item.get("query")
        params = item.get("params")

        try:
            with connect(**FEDERADA_CONF) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if not query.strip().lower().startswith("select"):
                        conn.commit()
                    logger.info("Consulta ejecutada correctamente: %s %s", query, params)
        except Error as exc:
            logger.warning("No se pudo ejecutar: %s %s → %s", query, params, exc)
            nuevos_pendientes.append(item)

    guardar_pendientes(nuevos_pendientes)
    logger.info("Sincronización terminada. Quedan %d pendientes.", len(nuevos_pendientes))


if __name__ == "__main__":
    configurar_logging()
    sincronizar()
