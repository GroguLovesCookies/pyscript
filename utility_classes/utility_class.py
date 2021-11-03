from typing import List, Type


class UtilityClass:
    default_values: List = []
    default = None

    def duplicate(self):
        return type(self)(*list(vars(self).values()))

    def set_attribute(self, name: str, value):
        new = self.duplicate()
        new.__setattr__(name, value)
        return new

    def set(self, key, value):
        self.__setattr__(key, value)


def initialize_class(class_name: Type):
    class_name.default = class_name(*class_name.default_values)
