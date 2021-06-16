import unittest
from tokens import split_list


class SplitTest(unittest.TestCase):
    def test_split(self):
        self.assertEqual(["1", "2", "3"], split_list("1,2,3", ","))

    def test_mississippi(self):
        self.assertEqual(["mi", "", "i", "", "ippi"], split_list("mississippi", "s"))

    def test_string_split(self):
        self.assertEqual(["Grogu", "Baby Yoda", "Mando, is good"],
                         split_list("\"Grogu\", \"Baby Yoda\", \"Mando, is good\"", ",", True))


if __name__ == '__main__':
    unittest.main()
