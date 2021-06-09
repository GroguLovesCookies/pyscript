global_vars = []


class Variable:
    def __init__(self, name, value, readonly=False):
        self.value = value
        self.name = name
        self.readonly = readonly

    def __str__(self):
        if not self.readonly:
            return f"{self.name} = {self.value}"
        else:
            return f"readonly {self.name} = {self.value}"


def create_var(name, value, readonly=False):
    global_vars.append(Variable(name, value, readonly))
    return global_vars[-1]


def set_var(name, value, readonly=False):
    for var in global_vars:
        if var.name == name:
            var.value = value
            return var.value
    return create_var(name, value, readonly)
