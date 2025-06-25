import os
import json
from mysql.connector import connect, Error
from utils.logger import logger


class GestorFragmentacionHorizontal:
    """Gestiona inserciones con respaldo local por fragmentos alfabéticos."""

    def __init__(self) -> None:
        self.federada_conf = {
            "host": os.getenv("DB_FRAG_HOST"),
            "port": int(os.getenv("DB_FRAG_PORT", 3306)),
            "database": os.getenv("DB_FRAG_NAME"),
            "user": os.getenv("DB_FRAG_USER"),
            "password": os.getenv("DB_FRAG_PASSWORD"),
        }
        self.local_am_conf = {
            "host": os.getenv("DB_LOCAL_AM_HOST"),
            "port": int(os.getenv("DB_LOCAL_AM_PORT", 3306)),
            "database": os.getenv("DB_LOCAL_AM_NAME"),
            "user": os.getenv("DB_LOCAL_AM_USER"),
            "password": os.getenv("DB_LOCAL_AM_PASSWORD"),
        }
        self.local_nz_conf = {
            "host": os.getenv("DB_LOCAL_NZ_HOST"),
            "port": int(os.getenv("DB_LOCAL_NZ_PORT", 3306)),
            "database": os.getenv("DB_LOCAL_NZ_NAME"),
            "user": os.getenv("DB_LOCAL_NZ_USER"),
            "password": os.getenv("DB_LOCAL_NZ_PASSWORD"),
        }
        self.queue_file = "pendientes_remota.json"
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def ejecutar(self, query: str, params=None):
        """Ejecutar inserción en la base federada con respaldo local."""
        try:
            with connect(**self.federada_conf) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if query.strip().lower().startswith("select"):
                        return cursor.fetchall()
                    conn.commit()
                    logger.info("Consulta ejecutada en bd_federada_cliente")
                    return True
        except Error as e:
            logger.warning(f"Fallo en BD federada: {e}")
            return self._respaldo_local(query, params)

    def _respaldo_local(self, query, params=None):
        nombre = params[1] if params and len(params) > 1 else ""
        letra = nombre.strip().upper()[:1]
        conf = self.local_am_conf if "A" <= letra <= "M" else self.local_nz_conf
        try:
            with connect(**conf) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if query.strip().lower().startswith("select"):
                        return cursor.fetchall()
                    conn.commit()
                    logger.info("Consulta ejecutada en base local de respaldo")
                    return True
        except Error as e:
            logger.error(f"No se pudo acceder a la BD local: {e}")
            self._registrar_pendiente(query, params)
            return None

    def _registrar_pendiente(self, query, params):
        try:
            with open(self.queue_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append({"query": query, "params": params})
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info("Consulta guardada en pendientes_remota.json")
        except Exception as exc:
            logger.error(f"No se pudo guardar en pendientes: {exc}")
