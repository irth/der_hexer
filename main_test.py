from re import A
import unittest
from main import Point


class TestPointMethods(unittest.TestCase):
    def test_substract(self):
        a = Point(4, 7)
        b = Point(1, 2)
        c = a - b
        self.assertAlmostEqual(c.x, 4 - 1)
        self.assertAlmostEqual(c.y, 7 - 2)

    def test_negative(self):
        a = Point(1, -2)
        b = -a
        self.assertAlmostEqual(b.x, -1)
        self.assertAlmostEqual(b.y, 2)

    def test_absolute(self):
        a = Point(1, -2)
        b = Point(-1, 2)

        a_abs = abs(a)
        b_abs = abs(b)

        self.assertAlmostEqual(a_abs.x, 1)
        self.assertAlmostEqual(a_abs.y, 2)
        self.assertAlmostEqual(b_abs.x, 1)
        self.assertAlmostEqual(b_abs.y, 2)

    def test_scale(self):
        a = Point(1, -2)
        b = a * 3
        c = a * 1.5
        d = 3 * a
        e = 1.5 * a

        self.assertAlmostEqual(b.x, 3)
        self.assertAlmostEqual(b.y, -6)
        self.assertAlmostEqual(c.x, 1.5)
        self.assertAlmostEqual(c.y, -3)
        self.assertAlmostEqual(d.x, 3)
        self.assertAlmostEqual(d.y, -6)
        self.assertAlmostEqual(e.x, 1.5)
        self.assertAlmostEqual(e.y, -3)


if __name__ == '__main__':
    unittest.main()
