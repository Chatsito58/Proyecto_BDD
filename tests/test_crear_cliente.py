import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.modules.setdefault('customtkinter', MagicMock())

from logica.clientes import crear_cliente, DatosClienteInvalidos


class CrearClienteTest(unittest.TestCase):
    @patch('logica.clientes.sha256_hash')
    @patch('logica.clientes.ConexionBD')
    def test_crear_cliente_exitoso(self, mock_conn_cls, mock_hash):
        mock_conn = MagicMock()
        mock_conn_cls.return_value = mock_conn
        mock_hash.return_value = 'hashed-secret'

        crear_cliente(
            '1', 'Ana', '123', 'Calle 1',
            'ana@example.com', 'secret', 'L1', 'TD', 'TC', 'CP'
        )

        mock_hash.assert_called_once_with('secret')
        mock_conn.ejecutar.assert_called_once()
        query, params = mock_conn.ejecutar.call_args[0]
        self.assertIn('INSERT INTO Cliente', query)
        self.assertEqual(params[5], 'hashed-secret')

    def test_validacion_correo(self):
        with self.assertRaises(DatosClienteInvalidos):
            crear_cliente(
                '1', 'Ana', '123', 'Calle 1',
                'correo-invalido', 'x', 'L1', 'TD', 'TC', 'CP'
            )

    def test_campos_obligatorios(self):
        with self.assertRaises(DatosClienteInvalidos):
            crear_cliente('', '', '', '', '', '', '', '', '', '')

    def test_campos_obligatorios_individual(self):
        valid = [
            '1', 'Ana', '123', 'Calle 1',
            'ana@example.com', 'secret', 'L1', 'TD', 'TC', 'CP'
        ]
        for idx in range(len(valid)):
            inval = valid.copy()
            inval[idx] = ''
            with self.subTest(field=idx):
                with self.assertRaises(DatosClienteInvalidos):
                    crear_cliente(*inval)


if __name__ == '__main__':
    unittest.main()
