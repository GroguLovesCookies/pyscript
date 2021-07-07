global_vars = []


class Variable:
    def __init__(self, name, value, readonly=False):
        self.value = value
        self.name = name
        self.readonly = readonly

    def __repr__(self):
        value = self.value
        if type(self.value) == str:
            value = f"\"{self.value}\""
        if not self.readonly:
            return f"{self.name} = {value}"
        else:
            return f"readonly {self.name} = {value}"


def create_var(name, value, readonly=False):
    global_vars.append(Variable(name, value, readonly))
    return global_vars[-1].value


def set_var(name, value, readonly=False):
    for var in global_vars:
        if var.name == name:
            var.value = value
            return var.value
    return create_var(name, value, readonly)


def index_set_var(name, value, indices):
    for var in global_vars:
        if var.name == name:
            element_stack = []
            i = 0
            element_stack.append(var.value)
            for index in indices:
                i += 1
                if i < len(indices)-1:
                    element_stack.append(element_stack[-1][index])
            i = 0
            for index in reversed(indices):
                element_stack[-1-i][index] = value
                i += 1
