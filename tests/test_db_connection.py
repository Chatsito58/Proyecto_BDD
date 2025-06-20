import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conexion.conexion import ConexionBD


class ConexionDBTest(unittest.TestCase):
    @patch('conexion.conexion.mysql.connector.connect')
    def test_conectar_exitoso(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_connect.return_value = mock_conn

        with patch.object(ConexionBD, '_cargar_pendientes', return_value=None), \
             patch.object(ConexionBD, '_guardar_pendientes', return_value=None), \
             patch.object(ConexionBD, '_sincronizar', return_value=None):
            db = ConexionBD()
            self.assertIs(db.conn, mock_conn)
            self.assertTrue(db.conn.is_connected())
            mock_connect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
