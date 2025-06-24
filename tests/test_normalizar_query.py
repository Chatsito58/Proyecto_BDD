import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Consulta import MySQLApp

class NormalizarQueryTest(unittest.TestCase):
    def test_keywords_inside_words_not_spaced(self):
        app = MySQLApp.__new__(MySQLApp)
        original = "INSERT INTO Tipo_documento (descripcion) VALUES ('Prueba documento');"
        result = app._normalizar_query(original)
        self.assertEqual(result, original)

if __name__ == '__main__':
    unittest.main()
