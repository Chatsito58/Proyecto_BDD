import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fragmentacion.gestor import GestorFragmentacion


class FragmentacionTest(unittest.TestCase):
    @patch('fragmentacion.gestor.ConexionBD')
    def test_ruta_id_par(self, mock_conn):
        frag1 = MagicMock()
        frag2 = MagicMock()
        mock_conn.side_effect = [frag1, frag2]
        gestor = GestorFragmentacion()
        gestor.ejecutar('INSERT INTO cliente VALUES (%s)', (2,))
        frag1.ejecutar.assert_called_once()
        frag2.ejecutar.assert_not_called()

    @patch('fragmentacion.gestor.ConexionBD')
    def test_ruta_id_impar(self, mock_conn):
        frag1 = MagicMock()
        frag2 = MagicMock()
        mock_conn.side_effect = [frag1, frag2]
        gestor = GestorFragmentacion()
        gestor.ejecutar('INSERT INTO cliente VALUES (%s)', (3,))
        frag2.ejecutar.assert_called_once()
        frag1.ejecutar.assert_not_called()


if __name__ == '__main__':
    unittest.main()
