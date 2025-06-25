import os
import json
from mysql.connector import connect, Error
from utils.logger import logger

class GestorRedundanciaRespaldo:
    def __init__(self):
        self.remote_conf = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        }

        self.local_conf = {
            "host": os.getenv("DB2_HOST"),
            "port": int(os.getenv("DB2_PORT")),
            "database": os.getenv("DB2_NAME"),
            "user": os.getenv("DB2_USER"),
            "password": os.getenv("DB2_PASSWORD")
        }

        self.respaldo_path = "pendientes_local.json"
        if not os.path.exists(self.respaldo_path):
            with open(self.respaldo_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def ejecutar(self, query: str, params=None):
        try:
            with connect(**self.remote_conf) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if query.strip().lower().startswith("select"):
                        return cursor.fetchall()
                    conn.commit()
                    return True
        except Error as e:
            logger.warning(f"Fallo en BD remota: {e}")
            return self._respaldo_local(query, params)

    def _respaldo_local(self, query, params=None):
        try:
            with connect(**self.local_conf) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if query.strip().lower().startswith("select"):
                        return cursor.fetchall()
                    conn.commit()
                    self._registrar_en_respaldo(query, params)
                    return True
        except Error as e:
            logger.error(f"No se pudo acceder a la BD local: {e}")
            self._registrar_en_respaldo(query, params)
            return None

    def _registrar_en_respaldo(self, query, params):
        try:
            with open(self.respaldo_path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append({"query": query, "params": params})
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info("Consulta guardada localmente en pendientes_local.json")
        except Exception as e:
            logger.error(f"No se pudo guardar en respaldo local: {e}")
