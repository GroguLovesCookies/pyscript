import sys


class Error:
    def __init__(self, err_type, msg, auto_throw=False):
        self.msg = msg
        self.type = err_type
        if auto_throw:
            self.throw()

    def throw(self):
        print(f"{self.type}: {self.msg}")
        sys.exit(1)


class PyscriptSyntaxError(Error):
    def __init__(self, msg, auto_throw=False):
        Error.__init__(self, "SyntaxError", msg, auto_throw)


class PyscriptNameError(Error):
    def __init__(self, msg, auto_throw=False):
        Error.__init__(self, "NameError", msg, auto_throw)


class PyscriptAssignmentError(Error):
    def __init__(self, msg, auto_throw=False):
        Error.__init__(self, "AssignmentError", msg, auto_throw)


class PyscriptIndexError(Error):
    def __init__(self, msg, auto_throw=False):
        Error.__init__(self, "IndexError", msg, auto_throw)


class PyscriptIndentationError(Error):
    def __init__(self, msg, auto_throw=False):
        Error.__init__(self, "IndentationError", msg, auto_throw)


class PyscriptAssertionError(Error):
    def __init__(self, auto_throw=False):
        Error.__init__(self, "AssertionError", "Assertion Failed", auto_throw)