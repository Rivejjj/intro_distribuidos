
import unittest

def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

class MiPrueba(unittest.TestCase):
    def test_suma(self):
        resultado = suma(2, 3)
        self.assertEqual(resultado, 4)

    def test_resta(self):
        resultado = resta(2, 3)
        self.assertEqual(resultado, 1000)

if __name__ == '__main__':
    unittest.main()
