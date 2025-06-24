import unittest
from unittest.mock import MagicMock
from mysql.connector import Error
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conexion.conexion import ConexionBD

class SyncFixTest(unittest.TestCase):
    def setUp(self):
        self.db = ConexionBD.__new__(ConexionBD)
        self.db.conn_local = MagicMock()
        self.db.conn_local.is_connected.return_value = True
        self.db.pendientes_local = []
        self.db.queue_file_local = '/tmp/pendientes_test_local.json'
        self.db._guardar_pendientes_local = MagicMock()

    def test_fix_clientes_query(self):
        cursor = MagicMock()
        self.db.conn_local.cursor.return_value = cursor
        err = Error(msg="1146 (42S02): Table 'alquiler_vehiculos.clientes' doesn't exist")
        cursor.execute.side_effect = err
        self.db.pendientes_local = [{
            'query': 'INSERT INTO clientes (nombre) VALUES (%s)',
            'params': ('Ana',),
        }]
        self.db._sincronizar_local()
        cursor.execute.assert_called_once_with('INSERT INTO clientes (nombre) VALUES (%s)', ('Ana',))
        self.assertEqual(self.db.pendientes_local[0]['query'], 'INSERT INTO clientes (nombre) VALUES (%s)')

    def test_fetch_select_results(self):
        cursor = MagicMock()
        self.db.conn_local.cursor.return_value = cursor
        self.db.pendientes_local = [{
            'query': 'SELECT * FROM cliente',
            'params': None,
        }]
        self.db._sincronizar_local()
        cursor.execute.assert_called_once_with('SELECT * FROM cliente', None)
        self.db.conn_local.commit.assert_not_called()
        cursor.close.assert_called_once()

    def test_fix_empleados_query(self):
        cursor = MagicMock()
        self.db.conn_local.cursor.return_value = cursor
        err = Error(msg="1146 (42S02): Table 'alquiler_vehiculos.empleados' doesn't exist")
        cursor.execute.side_effect = err
        self.db.pendientes_local = [{
            'query': 'INSERT INTO empleados (nombre) VALUES (%s)',
            'params': ('Ana',),
        }]
        self.db._sincronizar_local()
        cursor.execute.assert_called_once_with('INSERT INTO empleados (nombre) VALUES (%s)', ('Ana',))
        self.assertEqual(self.db.pendientes_local[0]['query'], 'INSERT INTO empleados (nombre) VALUES (%s)')

    def test_fetch_select_results(self):
        cursor = MagicMock()
        self.db.conn_local.cursor.return_value = cursor
        self.db.pendientes_local = [{
            'query': 'SELECT * FROM empleado',
            'params': None,
        }]
        self.db._sincronizar_local()
        cursor.execute.assert_called_once_with('SELECT * FROM empleado', None)
        self.db.conn_local.commit.assert_not_called()
        cursor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
 
