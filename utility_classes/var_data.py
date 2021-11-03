from utility_classes import utility_class
from errors import PyscriptSyntaxError
from typing import List


class VarData(utility_class.UtilityClass):
    default_values = [False, False, False, False, False, False]

    def __init__(self, is_del: bool, is_using: bool, is_out: bool, is_for: bool, is_func: bool, is_import: bool):
        self.is_del: bool = is_del
        self.is_using: bool = is_using
        self.is_out = is_out
        self.is_for = is_for
        self.is_func = is_func
        self.is_import = is_import
        self.check_errors()

    def check_errors(self):
        all_flags: List[bool] = [self.is_using, self.is_del, self.is_out, self.is_for, self.is_func, self.is_import]
        seen_true: bool = False
        for flag in all_flags:
            if flag:
                if not seen_true:
                    seen_true = True
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)

    def set(self, key: str, value):
        self.__setattr__(key, value)
        self.check_errors()


utility_class.initialize_class(VarData)
