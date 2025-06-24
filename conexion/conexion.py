"""Módulo de conexión a MySQL con failover y verificación de conexión."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Tuple

import mysql.connector
from mysql.connector import Error, MySQLConnection
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración externa remota (opcional)
remote_conf = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user2": os.getenv("DB2_USER"),
    "password2": os.getenv("DB2_PASSWORD"),
    "host2": os.getenv("DB2_HOST"),
    "port2": int(os.getenv("DB2_PORT")),
    "database2": os.getenv("DB2_NAME")
}

class DatabaseExecutionError(Exception):
    def __init__(self, query: str, original: Error) -> None:
        msg = f"Error ejecutando query '{query}': {original}"
        super().__init__(msg)
        self.query = query
        self.original = original

class ConexionBD:
    """Gestiona conexiones local y remota con colas de operaciones."""

    def __init__(
        self,
        *,
        queue_file_local: str = "pendientes_local.json",
        queue_file_remota: str = "pendientes_remota.json",
    ) -> None:
        """Inicializa las dos conexiones y sus colas."""

        load_dotenv()
        self.local_conf = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
        }
        self.remote_conf = {
            "host": os.getenv("DB2_HOST"),
            "user": os.getenv("DB2_USER"),
            "password": os.getenv("DB2_PASSWORD"),
            "database": os.getenv("DB2_NAME"),
        }

        self.conn_local: MySQLConnection | None = None
        self.conn_remota: MySQLConnection | None = None

        self.queue_file_local = queue_file_local
        self.queue_file_remota = queue_file_remota

        self._cargar_pendientes_local()
        self._cargar_pendientes_remota()

        self.conectar_remota()
        self.conectar_local()

    def conexion_valida_local(self) -> bool:
        """Verificar la conexión local."""
        return self.conn_local is not None and self.conn_local.is_connected()

    def conexion_valida_remota(self) -> bool:
        """Verificar la conexión remota."""
        return self.conn_remota is not None and self.conn_remota.is_connected()

    # ---- Manejo de pendientes ----
    def _cargar_pendientes_local(self) -> None:
        if os.path.exists(self.queue_file_local):
            with open(self.queue_file_local, "r", encoding="utf-8") as f:
                self.pendientes_local: List[dict[str, Any]] = json.load(f)
        else:
            self.pendientes_local = []

    def _cargar_pendientes_remota(self) -> None:
        if os.path.exists(self.queue_file_remota):
            with open(self.queue_file_remota, "r", encoding="utf-8") as f:
                self.pendientes_remota: List[dict[str, Any]] = json.load(f)
        else:
            self.pendientes_remota = []

    def _guardar_pendientes_local(self) -> None:
        with open(self.queue_file_local, "w", encoding="utf-8") as f:
            json.dump(self.pendientes_local, f, ensure_ascii=False, indent=2)
        logging.debug("Cola local escrita en %s", self.queue_file_local)

    def _guardar_pendientes_remota(self) -> None:
        with open(self.queue_file_remota, "w", encoding="utf-8") as f:
            json.dump(self.pendientes_remota, f, ensure_ascii=False, indent=2)
        logging.debug("Cola remota escrita en %s", self.queue_file_remota)

    # ---- Conexiones ----
    def conectar_local(self) -> None:
        try:
            self.conn_local = mysql.connector.connect(**self.local_conf)
            logging.info("Conectado a base local")
            self._sincronizar_local()
        except Error as e:
            logging.error("Error al conectar a base local: %s", e)
            self.conn_local = None

    def conectar_remota(self) -> None:
        try:
            self.conn_remota = mysql.connector.connect(**self.remote_conf)
            logging.info("Conectado a base remota")
            self._sincronizar_remota()
        except Error as e:
            logging.error("Error al conectar a base remota: %s", e)
            self.conn_remota = None

    def ejecutar(self, query: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
        """Ejecuta la consulta priorizando la base remota."""

        # ----- Intento en remota -----
        if not self.conexion_valida_remota():
            self.conectar_remota()
        if self.conexion_valida_remota():
            try:
                cur = self.conn_remota.cursor()
                cur.execute(query, params)
                if query.strip().lower().startswith("select"):
                    res = cur.fetchall()
                else:
                    self.conn_remota.commit()
                    res = []
                cur.close()
                logging.info("Consulta ejecutada en remota")
                return res
            except Error as e:
                logging.error("Error ejecutando en remota: %s", e)
                self._agregar_pendiente_remota(query, params)

        # ----- Fallback local -----
        if not self.conexion_valida_local():
            self.conectar_local()
        if self.conexion_valida_local():
            try:
                cur = self.conn_local.cursor()
                cur.execute(query, params)
                if query.strip().lower().startswith("select"):
                    res = cur.fetchall()
                else:
                    self.conn_local.commit()
                    res = []
                cur.close()
                logging.info("Consulta ejecutada en local")
                return res
            except Error as e:
                logging.error("Error ejecutando en local: %s", e)
                self._agregar_pendiente_local(query, params)
                raise DatabaseExecutionError(query, e) from e

        # No se pudo conectar a ninguna base
        self._agregar_pendiente_local(query, params)
        raise ConnectionError("No hay conexión disponible")

    def ejecutar_con_columnas(
        self, query: str, params: Tuple[Any, ...] | None = None
    ) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Versión con retorno de columnas."""

        # Intento en remota
        if not self.conexion_valida_remota():
            self.conectar_remota()
        if self.conexion_valida_remota():
            try:
                cur = self.conn_remota.cursor()
                cur.execute(query, params)
                columnas = [d[0] for d in cur.description] if cur.description else []
                filas = cur.fetchall() if query.strip().lower().startswith("select") else []
                self.conn_remota.commit()
                cur.close()
                logging.info("Consulta con columnas ejecutada en remota")
                return columnas, filas
            except Error as e:
                logging.error("Error ejecutando en remota: %s", e)
                self._agregar_pendiente_remota(query, params)

        # Fallback local
        if not self.conexion_valida_local():
            self.conectar_local()
        if self.conexion_valida_local():
            try:
                cur = self.conn_local.cursor()
                cur.execute(query, params)
                columnas = [d[0] for d in cur.description] if cur.description else []
                filas = cur.fetchall() if query.strip().lower().startswith("select") else []
                self.conn_local.commit()
                cur.close()
                logging.info("Consulta con columnas ejecutada en local")
                return columnas, filas
            except Error as e:
                logging.error("Error ejecutando en local: %s", e)
                self._agregar_pendiente_local(query, params)
                raise DatabaseExecutionError(query, e) from e

        self._agregar_pendiente_local(query, params)
        raise ConnectionError("No hay conexión disponible")

    # ---- Manejo de colas ----
    def _agregar_pendiente_local(self, query: str, params: Tuple[Any, ...] | None) -> None:
        self.pendientes_local.append({"query": query, "params": params})
        self._guardar_pendientes_local()
        logging.info("Consulta almacenada en pendientes local")

    def _agregar_pendiente_remota(self, query: str, params: Tuple[Any, ...] | None) -> None:
        self.pendientes_remota.append({"query": query, "params": params})
        self._guardar_pendientes_remota()
        logging.info("Consulta almacenada en pendientes remota")

    # ---- Sincronización ----
    def _sincronizar_local(self) -> None:
        if not self.pendientes_local or not self.conexion_valida_local():
            return
        logging.info(
            "Sincronizando %d operaciones pendientes (local)",
            len(self.pendientes_local),
        )
        while self.pendientes_local:
            op = self.pendientes_local.pop(0)
            try:
                cur = self.conn_local.cursor()
                cur.execute(op["query"], op["params"])
                if op["query"].strip().lower().startswith("select"):
                    cur.fetchall()
                else:
                    self.conn_local.commit()
                cur.close()
            except Error as e:
                logging.error("Error al sincronizar local: %s", e)
                corregida = None
                if "clientes" in op["query"].lower() and "doesn't exist" in str(e):
                    corregida = op["query"].replace("clientes", "Cliente")
                elif "empleados" in op["query"].lower() and "doesn't exist" in str(e):
                    corregida = op["query"].replace("empleados", "empleado")
                if corregida:
                    logging.info("Reintentando con tabla: %s", corregida)
                    try:
                        cur.execute(corregida, op["params"])
                        if corregida.strip().lower().startswith("select"):
                            cur.fetchall()
                        else:
                            self.conn_local.commit()
                        cur.close()
                        continue
                    except Error as e2:
                        logging.error("Error tras corregir: %s", e2)
                        op["query"] = corregida
                self.pendientes_local.insert(0, op)
                break
        self._guardar_pendientes_local()

    def _sincronizar_remota(self) -> None:
        if not self.pendientes_remota or not self.conexion_valida_remota():
            return
        logging.info(
            "Sincronizando %d operaciones pendientes (remota)",
            len(self.pendientes_remota),
        )
        while self.pendientes_remota:
            op = self.pendientes_remota.pop(0)
            try:
                cur = self.conn_remota.cursor()
                cur.execute(op["query"], op["params"])
                if op["query"].strip().lower().startswith("select"):
                    cur.fetchall()
                else:
                    self.conn_remota.commit()
                cur.close()
            except Error as e:
                logging.error("Error al sincronizar remota: %s", e)
                corregida = None
                if "clientes" in op["query"].lower() and "doesn't exist" in str(e):
                    corregida = op["query"].replace("clientes", "Cliente")
                elif "empleados" in op["query"].lower() and "doesn't exist" in str(e):
                    corregida = op["query"].replace("empleados", "empleado")
                if corregida:
                    logging.info("Reintentando con tabla: %s", corregida)
                    try:
                        cur.execute(corregida, op["params"])
                        if corregida.strip().lower().startswith("select"):
                            cur.fetchall()
                        else:
                            self.conn_remota.commit()
                        cur.close()
                        continue
                    except Error as e2:
                        logging.error("Error tras corregir: %s", e2)
                        op["query"] = corregida
                self.pendientes_remota.insert(0, op)
                break
        self._guardar_pendientes_remota()

    def _sincronizar(self) -> None:
        self._sincronizar_remota()
        self._sincronizar_local()

    # ---- Cierre ----
    def close(self) -> None:
        if self.conexion_valida_remota():
            self._sincronizar_remota()
            self.conn_remota.close()
            self.conn_remota = None
            logging.info("Conexión remota cerrada")
        if self.conexion_valida_local():
            self._sincronizar_local()
            self.conn_local.close()
            self.conn_local = None
            logging.info("Conexión local cerrada")

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
