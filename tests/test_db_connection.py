import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conexion.conexion import ConexionBD


class ConexionDBTest(unittest.TestCase):
    @patch('conexion.conexion.mysql.connector.connect')
    def test_conectar_exitoso(self, mock_connect):
        conn_remote = MagicMock()
        conn_remote.is_connected.return_value = True
        conn_local = MagicMock()
        conn_local.is_connected.return_value = True
        mock_connect.side_effect = [conn_remote, conn_local]

        with patch.object(ConexionBD, '_cargar_pendientes_local', return_value=None), \
             patch.object(ConexionBD, '_cargar_pendientes_remota', return_value=None), \
             patch.object(ConexionBD, '_guardar_pendientes_local', return_value=None), \
             patch.object(ConexionBD, '_guardar_pendientes_remota', return_value=None), \
             patch.object(ConexionBD, '_sincronizar_local', return_value=None), \
             patch.object(ConexionBD, '_sincronizar_remota', return_value=None):
            db = ConexionBD()
            self.assertIs(db.conn_remota, conn_remote)
            self.assertIs(db.conn_local, conn_local)
            self.assertTrue(db.conn_remota.is_connected())
            self.assertTrue(db.conn_local.is_connected())
            self.assertEqual(mock_connect.call_count, 2)


if __name__ == '__main__':
    unittest.main()
