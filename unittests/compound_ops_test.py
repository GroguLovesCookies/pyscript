import unittest
from tokens import compound_operators, read


class CompoundOpsTest(unittest.TestCase):
    def test_read(self):
        tokenized, raw, count = read("not in")
        self.assertEqual([token.val for token in raw], ["not", "in"])

    def test_compound(self):
        tokenized, raw, count = read("not in")
        self.assertEqual([token.val for token in compound_operators(raw)], ["not in"])


if __name__ == '__main__':
    unittest.main()
