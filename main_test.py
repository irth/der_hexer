import unittest
from main import Point


class TestPointMethods(unittest.TestCase):
    def test_substract(self):
        a = Point(4, 7)
        b = Point(1, 2)
        c = a - b
        self.assertEqual(c.x, 4 - 1)
        self.assertEqual(c.y, 7 - 2)

    def test_negative(self):
        a = Point(1, -2)
        b = -a
        self.assertEqual(b.x, -1)
        self.assertEqual(b.y, 2)

    def test_absolute(self):
        a = Point(1, -2)
        b = Point(-1, 2)

        a_abs = abs(a)
        b_abs = abs(b)

        self.assertEqual(a_abs.x, 1)
        self.assertEqual(a_abs.y, 2)
        self.assertEqual(b_abs.x, 1)
        self.assertEqual(b_abs.y, 2)


if __name__ == '__main__':
    unittest.main()
