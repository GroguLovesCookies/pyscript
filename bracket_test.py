import unittest
from tokens import bracket_extract, read, get_closing


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(4, get_closing(read("(2*2)")))


if __name__ == '__main__':
    unittest.main()
