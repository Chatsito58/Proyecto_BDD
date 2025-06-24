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
    """Manejo de conexión MySQL con failover, cola de operaciones y prueba de conexión."""

    def __init__(self, *, active: str = "remote", queue_file: str = "pendientes.json") -> None:
        """Inicializa la conexión.

        Parameters
        ----------
        active:
            Indica qué base usar inicialmente, ``"remote"`` o ``"local"``.
        queue_file:
            Ruta del archivo donde se almacenarán las operaciones pendientes.
        """
        load_dotenv()
        self.local_conf = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
        }
        self.remote_conf = {
            'host': os.getenv('DB2_HOST'),
            'user': os.getenv('DB2_USER'),
            'password': os.getenv('DB2_PASSWORD'),
            'database': os.getenv('DB2_NAME'),
        }
        self.active = active
        self.conn: MySQLConnection | None = None
        self.queue_file = queue_file
        self._cargar_pendientes()
        self.conectar()

    def conexion_valida(self) -> bool:
        """Verifica si la conexión actual es válida y activa."""
        return self.conn is not None and self.conn.is_connected()

    def _cargar_pendientes(self) -> None:
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                self.pendientes: List[dict[str, Any]] = json.load(f)
        else:
            self.pendientes = []

    def _guardar_pendientes(self) -> None:
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.pendientes, f, ensure_ascii=False, indent=2)

    def conectar(self) -> None:
        config = self.local_conf if self.active == 'local' else self.remote_conf
        try:
            self.conn = mysql.connector.connect(**config)
            logging.info('Conectado a base %s', self.active)
            self._sincronizar()
        except Error as e:
            logging.error('Error al conectar a base %s: %s', self.active, e)
            self._failover()

    def _failover(self) -> None:
        self.active = 'remote' if self.active == 'local' else 'local'
        config = self.local_conf if self.active == 'local' else self.remote_conf
        try:
            self.conn = mysql.connector.connect(**config)
            logging.info('Conmutación a base %s exitosa', self.active)
            self._sincronizar()
        except Error as e:
            logging.error('Failover fallido: %s', e)
            self.conn = None

    def ejecutar(self, query: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
        if not self.conn or not self.conn.is_connected():
            self.conectar()
        if not self.conn:
            self._agregar_pendiente(query, params)
            raise ConnectionError('No hay conexión disponible')

        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            if query.strip().lower().startswith('select'):
                resultados = cur.fetchall()
            else:
                self.conn.commit()
                resultados = []
            return resultados
        except Error as e:
            logging.error('Error ejecutando consulta: %s', e)
            self._agregar_pendiente(query, params)
            self._failover()
            raise DatabaseExecutionError(query, e) from e
        finally:
            if cur:
                try:
                    if cur.with_rows and cur.fetchone() is not None:
                        cur.fetchall()
                except Error:
                    pass
                cur.close()

    def ejecutar_con_columnas(self, query: str, params: Tuple[Any, ...] | None = None) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        if not self.conn or not self.conn.is_connected():
            self.conectar()
        if not self.conn:
            self._agregar_pendiente(query, params)
            raise ConnectionError("No hay conexión disponible")

        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            columnas = [desc[0] for desc in cur.description] if cur.description else []
            filas = cur.fetchall() if query.strip().lower().startswith("select") else []
            self.conn.commit()
            cur.close()
            return columnas, filas
        except Error as e:
            logging.error("Error ejecutando consulta: %s", e)
            self._agregar_pendiente(query, params)
            self._failover()
            raise DatabaseExecutionError(query, e) from e

    def _agregar_pendiente(self, query: str, params: Tuple[Any, ...] | None) -> None:
        self.pendientes.append({'query': query, 'params': params})
        self._guardar_pendientes()
        logging.info('Consulta almacenada en cola de pendientes')

    def _sincronizar(self) -> None:
        if not self.pendientes or not self.conn or not self.conn.is_connected():
            return
        logging.info('Sincronizando %d operaciones pendientes', len(self.pendientes))
        while self.pendientes:
            op = self.pendientes.pop(0)
            try:
                cur = self.conn.cursor()
                cur.execute(op['query'], op['params'])
                if op['query'].strip().lower().startswith('select'):
                    cur.fetchall()
                else:
                    self.conn.commit()
                cur.close()
            except Error as e:
                logging.error('Error al sincronizar: %s', e)
                corregida = None
                if "clientes" in op['query'].lower() and "doesn't exist" in str(e):
                    corregida = op['query'].replace('clientes', 'Cliente')
                elif "empleados" in op['query'].lower() and "doesn't exist" in str(e):
                    corregida = op['query'].replace('empleados', 'empleado')
                if corregida:
                    logging.info('Reintentando con tabla: %s', corregida)
                    try:
                        cur.execute(corregida, op['params'])
                        if corregida.strip().lower().startswith('select'):
                            cur.fetchall()
                        else:
                            self.conn.commit()
                        cur.close()
                        continue
                    except Error as e2:
                        logging.error('Error tras corregir: %s', e2)
                        op['query'] = corregida
                self.pendientes.insert(0, op)
                break
        self._guardar_pendientes()

    def close(self) -> None:
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.conn = None
            logging.info("Conexión cerrada")

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
