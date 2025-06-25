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
    """Gestiona conexiones local y remota con colas de operaciones.

    Parameters
    ----------
    failover : bool, optional
        Si es ``True`` se intentará ejecutar la operación en la base secundaria
        cuando falle la primaria.
    """

    def __init__(
        self,
        active: str = "local",
        queue_file_local: str = "pendientes_local.json",
        queue_file_remota: str = "pendientes_remota.json",
        failover: bool = True,
    ) -> None:
        load_dotenv()
        self.queue_file_local = queue_file_local
        self.queue_file_remota = queue_file_remota
        self.active = active
        self.failover = failover

        self.local_conf = {
            'host': os.getenv('DB1_HOST'),
            'user': os.getenv('DB1_USER'),
            'password': os.getenv('DB1_PASSWORD'),
            'database': os.getenv('DB1_NAME'),
        }
        self.remote_conf = {
            'host': os.getenv('DB2_HOST'),
            'user': os.getenv('DB2_USER'),
            'password': os.getenv('DB2_PASSWORD'),
            'database': os.getenv('DB2_NAME'),
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
        """Ejecutar una consulta priorizando la base indicada en ``self.active``."""

        def _exec(db: str) -> List[Tuple[Any, ...]]:
            if db == "local":
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
                    except Error as err:
                        raise DatabaseExecutionError(query, err) from err
                raise ConnectionError("No hay conexión disponible")
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
                except Error as err:
                    raise DatabaseExecutionError(query, err) from err
            raise ConnectionError("No hay conexión disponible")

        primary = "local" if self.active == "local" else "remote"
        if primary == "remote" and self.active == "remota":
            primary = "remote"
        secondary = "remote" if primary == "local" else "local"

        try:
            return _exec(primary)
        except (DatabaseExecutionError, ConnectionError) as e:
            if self.failover:
                try:
                    return _exec(secondary)
                except (DatabaseExecutionError, ConnectionError):
                    if primary == "local":
                        self._agregar_pendiente_local(query, params)
                    else:
                        self._agregar_pendiente_remota(query, params)
                    raise
            else:
                if primary == "local":
                    self._agregar_pendiente_local(query, params)
                else:
                    self._agregar_pendiente_remota(query, params)
                raise

    def ejecutar_con_columnas(
        self, query: str, params: Tuple[Any, ...] | None = None
    ) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Versión de :meth:`ejecutar` que también devuelve las columnas."""

        def _exec(db: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
            if db == "local":
                if not self.conexion_valida_local():
                    self.conectar_local()
                if self.conexion_valida_local():
                    try:
                        cur = self.conn_local.cursor()
                        cur.execute(query, params)
                        cols = [d[0] for d in cur.description] if cur.description else []
                        rows = cur.fetchall() if query.strip().lower().startswith("select") else []
                        self.conn_local.commit()
                        cur.close()
                        return cols, rows
                    except Error as err:
                        raise DatabaseExecutionError(query, err) from err
                raise ConnectionError("No hay conexión disponible")

            if not self.conexion_valida_remota():
                self.conectar_remota()
            if self.conexion_valida_remota():
                try:
                    cur = self.conn_remota.cursor()
                    cur.execute(query, params)
                    cols = [d[0] for d in cur.description] if cur.description else []
                    rows = cur.fetchall() if query.strip().lower().startswith("select") else []
                    self.conn_remota.commit()
                    cur.close()
                    return cols, rows
                except Error as err:
                    raise DatabaseExecutionError(query, err) from err
            raise ConnectionError("No hay conexión disponible")

        primary = "local" if self.active == "local" else "remote"
        if primary == "remote" and self.active == "remota":
            primary = "remote"
        secondary = "remote" if primary == "local" else "local"

        try:
            return _exec(primary)
        except (DatabaseExecutionError, ConnectionError):
            if self.failover:
                try:
                    return _exec(secondary)
                except (DatabaseExecutionError, ConnectionError):
                    if primary == "local":
                        self._agregar_pendiente_local(query, params)
                    else:
                        self._agregar_pendiente_remota(query, params)
                    raise
            else:
                if primary == "local":
                    self._agregar_pendiente_local(query, params)
                else:
                    self._agregar_pendiente_remota(query, params)
                raise

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
        if not self.failover:
            return

        secondary = "remote" if self.active == "local" else "local"
        if secondary == "remote":
            self._sincronizar_remota()
        else:
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