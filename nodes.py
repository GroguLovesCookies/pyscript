class Node:
    def get_value(self):
        pass


class BinOpNode(Node):
    """A class to define operators"""
    def __init__(self, operand_a, operand_b, symbol, evaluation):
        self.operand_a = operand_a
        self.operand_b = operand_b
        self.symbol = symbol
        self.evaluation = evaluation

    def __repr__(self):
        return f"{self.operand_a} {self.symbol} {self.operand_b}"

    def get_value(self):
        """A function to calculate the value of a node"""

        # This is a recursive data structure: the
        # nodes can be either operators or integers
        if type(self.operand_a) == BinOpNode or type(self.operand_a) == UnOpNode:
            self.operand_a = self.operand_a.get_value()
        if type(self.operand_b) == BinOpNode or type(self.operand_b) == UnOpNode:
            self.operand_b = self.operand_b.get_value()

        return self.evaluation(self.operand_a, self.operand_b)


class UnOpNode(Node):
    """A class to define operators taking in one value"""
    def __init__(self, operand, symbol, evaluation):
        self.operand = operand
        self.symbol = symbol
        self.evaluation = evaluation

    def __repr__(self):
        return f"{self.symbol} {self.operand}"

    def get_value(self):
        if type(self.operand) == BinOpNode or type(self.operand) == UnOpNode:
            self.operand = self.operand.get_value()

        return self.evaluation(self.operand)


class ValueNode(Node):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __repr__(self):
        return f"{self.value}"
