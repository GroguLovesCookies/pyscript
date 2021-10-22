from utility_classes import utility_class
from errors import PyscriptSyntaxError


class VarData(utility_class.UtilityClass):
    default_values = [False, False, False]

    def __init__(self, is_del: bool, is_using: bool, is_out: bool):
        self.is_del: bool = is_del
        self.is_using: bool = is_using
        self.is_out = is_out
        self.check_errors()

    def check_errors(self):
        all_flags: List[bool] = [self.is_using, self.is_del, self.is_out]
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
