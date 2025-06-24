import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conexion.conexion import ConexionBD


class FailoverBehaviorTest(unittest.TestCase):
    @patch('conexion.conexion.mysql.connector.connect')
    def test_queue_when_primary_down_no_secondary(self, mock_connect):
        with patch.object(ConexionBD, '_cargar_pendientes_local', return_value=None), \
             patch.object(ConexionBD, '_cargar_pendientes_remota', return_value=None), \
             patch.object(ConexionBD, '_guardar_pendientes_local', return_value=None), \
             patch.object(ConexionBD, '_guardar_pendientes_remota', return_value=None):
            db = ConexionBD(active='local', failover=False)

        with patch.object(db, 'conexion_valida_local', return_value=False), \
             patch.object(db, 'conectar_local', return_value=None), \
             patch.object(db, 'conectar_remota') as mock_rem, \
             patch.object(db, '_agregar_pendiente_local') as mock_queue:
            with self.assertRaises(ConnectionError):
                db.ejecutar('INSERT INTO t VALUES (1)')
            mock_rem.assert_not_called()
            mock_queue.assert_called_once_with('INSERT INTO t VALUES (1)', None)


if __name__ == '__main__':
    unittest.main()
