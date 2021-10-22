from errors import PyscriptNameError


global_vars = []
cached = []
current_scope_pointer = -1


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


def shift_scope_pointer(i):
    global current_scope_pointer
    current_scope_pointer += i


def set_scope_pointer(i):
    global current_scope_pointer
    current_scope_pointer = i


def get_var_from_previous_scope(name):
    for var in cached[current_scope_pointer]:
        if var.name == name:
            set_scope_pointer(-1)
            return var.value
    PyscriptNameError(f"variable '{name}' was referenced before assignment", True)


def remove_var(name):
    i = 0
    while i < len(global_vars):
        if global_vars[i].name == name:
            val = global_vars[i]
            del global_vars[i]
            return val
        i += 1
    PyscriptNameError(f"variable '{name}' was referenced before assignment", True)


def start_new_scope():
    cached.append([])
    for var in global_vars:
        cached[-1].append(Variable(var.name, var.value, var.readonly))
    global_vars.clear()


def revert_from_scope():
    global global_vars
    global_vars.clear()
    for var in cached[-1]:
        create_var(var.name, var.value, var.readonly)
    del cached[-1]


def push_to_previous_cache(name):
    removed = remove_var(name)
    create_var(removed.name, removed.value, removed.readonly)
    for var in cached[-1]:
        if var.name == name:
            var.value = removed.value
            return
    cached[-1].append(removed)


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
