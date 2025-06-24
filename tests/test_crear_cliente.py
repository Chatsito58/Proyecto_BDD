import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.modules.setdefault('customtkinter', MagicMock())

from logica.clientes import crear_cliente, DatosClienteInvalidos
from utils.hash_utils import sha256_hash


class CrearClienteTest(unittest.TestCase):
    @patch('logica.clientes.ConexionBD')
    def test_crear_cliente_exitoso(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn_cls.return_value = mock_conn

        crear_cliente(
            '1', 'Ana', '123', 'Calle 1',
            'ana@example.com', 'secret', 'L1', 'TD', 'TC', 'CP'
        )

        mock_conn.ejecutar.assert_called_once()
        args = mock_conn.ejecutar.call_args[0]
        params = args[1]
        self.assertEqual(params[5], sha256_hash('secret'))

    def test_validacion_correo(self):
        with self.assertRaises(DatosClienteInvalidos):
            crear_cliente(
                '1', 'Ana', '123', 'Calle 1',
                'correo-invalido', 'x', 'L1', 'TD', 'TC', 'CP'
            )

    def test_campos_obligatorios(self):
        with self.assertRaises(DatosClienteInvalidos):
            crear_cliente('', '', '', '', '', '', '', '', '', '')


if __name__ == '__main__':
    unittest.main()
