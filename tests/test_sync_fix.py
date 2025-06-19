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
        self.db.conn = MagicMock()
        self.db.conn.is_connected.return_value = True
        self.db.pendientes = []
        self.db.queue_file = '/tmp/pendientes_test.json'

    def test_fix_clientes_query(self):
        cursor = MagicMock()
        self.db.conn.cursor.return_value = cursor
        err = Error(msg="1146 (42S02): Table 'alquiler_vehiculos.clientes' doesn't exist")
        cursor.execute.side_effect = [err, None]
        self.db.pendientes = [{
            'query': 'INSERT INTO clientes (nombre) VALUES (%s)',
            'params': ('Ana',)
        }]
        self.db._sincronizar()
        self.assertEqual(cursor.execute.call_args_list[1][0][0],
                         'INSERT INTO cliente (nombre) VALUES (%s)')

    def test_fetch_select_results(self):
        cursor = MagicMock()
        self.db.conn.cursor.return_value = cursor
        cursor.execute.side_effect = [None]
        cursor.fetchall.return_value = [(1,)]
        self.db.pendientes = [{
            'query': 'SELECT * FROM cliente',
            'params': None,
        }]
        self.db._sincronizar()
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()

    def test_fix_empleados_query(self):
        cursor = MagicMock()
        self.db.conn.cursor.return_value = cursor
        err = Error(msg="1146 (42S02): Table 'alquiler_vehiculos.empleados' doesn't exist")
        cursor.execute.side_effect = [err, None]
        self.db.pendientes = [{
            'query': 'INSERT INTO empleados (nombre) VALUES (%s)',
            'params': ('Ana',)
        }]
        self.db._sincronizar()
        self.assertEqual(cursor.execute.call_args_list[1][0][0],
                         'INSERT INTO empleado (nombre) VALUES (%s)')

    def test_fetch_select_results(self):
        cursor = MagicMock()
        self.db.conn.cursor.return_value = cursor
        cursor.execute.side_effect = [None]
        cursor.fetchall.return_value = [(1,)]
        self.db.pendientes = [{
            'query': 'SELECT * FROM empleado',
            'params': None,
        }]
        self.db._sincronizar()
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
 