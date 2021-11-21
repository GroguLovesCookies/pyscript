import unittest
from tokens import bracket_extract, read, get_closing, bracketize, prep_unary, unwrap_unary


class BracketTest(unittest.TestCase):
    def test_closing(self):
        self.assertEqual(4, get_closing(read("(2*2)")))

    def test_brackets(self):
        print(prep_unary())
        self.assertEqual(2, 2)


if __name__ == '__main__':
    unittest.main()
