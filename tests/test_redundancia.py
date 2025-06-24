import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from redundancia.gestor import GestorRedundancia


class RedundanciaTest(unittest.TestCase):
    @patch('redundancia.gestor.ConexionBD')
    def test_ejecutar_en_ambas_bases(self, mock_conn):
        local = MagicMock()
        remote = MagicMock()
        mock_conn.side_effect = [local, remote]
        gestor = GestorRedundancia()
        gestor.ejecutar('INSERT INTO t VALUES (%s)', (1,))
        local.ejecutar.assert_called_once_with('INSERT INTO t VALUES (%s)', (1,))
        remote.ejecutar.assert_called_once_with('INSERT INTO t VALUES (%s)', (1,))

    @patch('redundancia.gestor.ConexionBD')
    def test_ejecutar_con_columnas_fallback_local(self, mock_conn):
        local = MagicMock()
        local.ejecutar_con_columnas.return_value = (['id'], [(1,)])
        remote = MagicMock()
        remote.ejecutar_con_columnas.side_effect = Exception('fail')
        mock_conn.side_effect = [local, remote]
        gestor = GestorRedundancia()
        cols, rows = gestor.ejecutar_con_columnas('SELECT 1')
        self.assertEqual(cols, ['id'])
        self.assertEqual(rows, [(1,)])


if __name__ == '__main__':
    unittest.main()
