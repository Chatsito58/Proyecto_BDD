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
        active: str = "remota",
        queue_file_local: str = "pendientes_local.json",
        queue_file_remota: str = "pendientes_remota.json"
    ) -> None:
        load_dotenv()
        self.queue_file_local = queue_file_local
        self.queue_file_remota = queue_file_remota
        self.active = active

        self.local_conf = {
            'host': os.getenv('DB1_HOST', 'localhost'),
            'user': os.getenv('DB1_USER', 'root'),
            'password': os.getenv('DB1_PASSWORD', 'admin123'),
            'database': os.getenv('DB1_NAME', 'alquiler_vehiculos'),
        }
        self.remote_conf = {
            'host': os.getenv('DB2_HOST', '192.168.50.1'),
            'user': os.getenv('DB2_USER', 'usuario_bdd'),
            'password': os.getenv('DB2_PASSWORD', 'admin123'),
            'database': os.getenv('DB2_NAME', 'alquiler_vehiculos'),
        }

        self.conn_local: MySQLConnection | None = None
        self.conn_remota: MySQLConnection | None = None

        self._cargar_pendientes_local()
        self._cargar_pendientes_remota()
        self._sincronizar()

    def conexion_valida_local(self) -> bool:
        return self.conn_local is not None and self.conn_local.is_connected()

    def conexion_valida_remota(self) -> bool:
        return self.conn_remota is not None and self.conn_remota.is_connected()

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

    def _guardar_pendientes_remota(self) -> None:
        with open(self.queue_file_remota, "w", encoding="utf-8") as f:
            json.dump(self.pendientes_remota, f, ensure_ascii=False, indent=2)

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
        if not self.conexion_valida_remota():
            self.conectar_remota()
        if self.conexion_valida_remota():
            try:
                cur = self.conn_remota.cursor()
                cur.execute(query, params)
                res = cur.fetchall() if query.strip().lower().startswith("select") else []
                if not res:
                    self.conn_remota.commit()
                cur.close()
                return res
            except Error as e:
                self._agregar_pendiente_remota(query, params)

        if not self.conexion_valida_local():
            self.conectar_local()
        if self.conexion_valida_local():
            try:
                cur = self.conn_local.cursor()
                cur.execute(query, params)
                res = cur.fetchall() if query.strip().lower().startswith("select") else []
                if not res:
                    self.conn_local.commit()
                cur.close()
                return res
            except Error as e:
                self._agregar_pendiente_local(query, params)
                raise DatabaseExecutionError(query, e) from e

        self._agregar_pendiente_local(query, params)
        raise ConnectionError("No hay conexión disponible")

    def ejecutar_con_columnas(
        self, query: str, params: Tuple[Any, ...] | None = None
    ) -> Tuple[List[str], List[Tuple[Any, ...]]]:
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
                return columnas, filas
            except Error as e:
                self._agregar_pendiente_remota(query, params)

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
                return columnas, filas
            except Error as e:
                self._agregar_pendiente_local(query, params)
                raise DatabaseExecutionError(query, e) from e

        self._agregar_pendiente_local(query, params)
        raise ConnectionError("No hay conexión disponible")

    def _agregar_pendiente_local(self, query: str, params: Tuple[Any, ...] | None) -> None:
        self.pendientes_local.append({"query": query, "params": params})
        self._guardar_pendientes_local()

    def _agregar_pendiente_remota(self, query: str, params: Tuple[Any, ...] | None) -> None:
        self.pendientes_remota.append({"query": query, "params": params})
        self._guardar_pendientes_remota()

    def _sincronizar_local(self) -> None:
        if not self.pendientes_local or not self.conexion_valida_local():
            return
        while self.pendientes_local:
            op = self.pendientes_local.pop(0)
            try:
                cur = self.conn_local.cursor()
                cur.execute(op["query"], op["params"])
                if not op["query"].strip().lower().startswith("select"):
                    self.conn_local.commit()
                cur.close()
            except Error as e:
                self.pendientes_local.insert(0, op)
                break
        self._guardar_pendientes_local()

    def _sincronizar_remota(self) -> None:
        if not self.pendientes_remota or not self.conexion_valida_remota():
            return
        while self.pendientes_remota:
            op = self.pendientes_remota.pop(0)
            try:
                cur = self.conn_remota.cursor()
                cur.execute(op["query"], op["params"])
                if not op["query"].strip().lower().startswith("select"):
                    self.conn_remota.commit()
                cur.close()
            except Error as e:
                self.pendientes_remota.insert(0, op)
                break
        self._guardar_pendientes_remota()

    def _sincronizar(self) -> None:
        self._sincronizar_remota()
        self._sincronizar_local()

    def close(self) -> None:
        if self.conexion_valida_remota():
            self._sincronizar_remota()
            self.conn_remota.close()
            self.conn_remota = None
        if self.conexion_valida_local():
            self._sincronizar_local()
            self.conn_local.close()
            self.conn_local = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass