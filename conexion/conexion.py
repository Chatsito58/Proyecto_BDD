import json
import logging
import os
from typing import Any, List, Tuple

import mysql.connector
from mysql.connector import MySQLConnection, Error
from dotenv import load_dotenv


class ConexionBD:
    """Manejo de dos conexiones MySQL con failover y cola de operaciones."""

    def __init__(self) -> None:
        load_dotenv()
        self.local_conf = {
            'host': os.getenv('DB1_HOST', '127.0.0.1'),
            'user': os.getenv('DB1_USER', 'root'),
            'password': os.getenv('DB1_PASSWORD', ''),
            'database': os.getenv('DB1_NAME', 'alquiler_vehiculos'),
        }
        self.remote_conf = {
            'host': os.getenv('DB2_HOST', '192.168.0.2'),
            'user': os.getenv('DB2_USER', 'root'),
            'password': os.getenv('DB2_PASSWORD', ''),
            'database': os.getenv('DB2_NAME', 'alquiler_vehiculos'),
        }
        self.active = 'local'
        self.conn: MySQLConnection | None = None
        self.queue_file = 'pendientes.json'
        self._cargar_pendientes()
        self.conectar()

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
            raise

    def ejecutar_con_columnas(
        self, query: str, params: Tuple[Any, ...] | None = None
    ) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Ejecutar una consulta y retornar columnas y filas."""
        if not self.conn or not self.conn.is_connected():
            self.conectar()
        if not self.conn:
            self._agregar_pendiente(query, params)
            raise ConnectionError("No hay conexión disponible")
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            columnas = [desc[0] for desc in cur.description] if cur.description else []
            if query.strip().lower().startswith("select"):
                filas = cur.fetchall()
            else:
                self.conn.commit()
                filas = []
            cur.close()
            return columnas, filas
        except Error as e:
            logging.error("Error ejecutando consulta: %s", e)
            self._agregar_pendiente(query, params)
            self._failover()
            raise

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
                if (
                    "clientes" in op['query'].lower()
                    and "doesn't exist" in str(e)
                ):
                    corregida = op['query'].replace('clientes', 'cliente')
                elif (
                    "empleados" in op['query'].lower()
                    and "doesn't exist" in str(e)
                ):
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
                    except Error as e2:  # pragma: no cover - depende de MySQL
                        logging.error('Error tras corregir: %s', e2)
                        op['query'] = corregida
                self.pendientes.insert(0, op)
                break
        self._guardar_pendientes()
