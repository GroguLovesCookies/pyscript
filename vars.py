from errors import PyscriptNameError
from structures.sorted_list import SortedList
import time


global_vars = SortedList()
cached = []
current_scope_pointer = -1
current_var = None
current_index = -1
# 0: linear, 1: binary, 2: interpolation
search_mode = 2


class Variable:
    def __init__(self, name, value, readonly=False):
        self.value = value
        self.name = name
        self.readonly = readonly
        self.name_val = 0
        for letter in self.name:
            self.name_val += ord(letter)

    def __repr__(self):
        value = self.value
        if type(self.value) == str:
            value = f"\"{self.value}\""
        if not self.readonly:
            return f"{self.name} = {value}"
        else:
            return f"readonly {self.name} = {value}"

    def __lt__(self, other):
        return self.name < other

    def __gt__(self, other):
        return self.name > other

    def __le__(self, other):
        return self.name <= other

    def __ge__(self, other):
        return self.name >= other

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __add__(self, other):
        if type(other) == Variable:
            op_val = other.name_val
        elif type(other) == str:
            op_val = 0
            for letter in other:
                op_val += ord(letter)
        return self.name_val + op_val

    def __sub__(self, other):
        if type(other) == Variable:
            op_val = other.name_val
        elif type(other) == str:
            op_val = 0
            for letter in other:
                op_val += ord(letter)
        return self.name_val - op_val

    def __mul__(self, other):
        if type(other) == Variable:
            op_val = other.name_val
        elif type(other) == str:
            op_val = 0
            for letter in other:
                op_val += ord(letter)
        return self.name_val * op_val


def create_var(name, value, readonly=False):
    global_vars.append(Variable(name, value, readonly))
    return global_vars[-1].value


def search_for_var(name):
    global current_var, current_index
    if search_mode == 0:
        i = 0
        for var in global_vars:
            if var == name:
                current_var = var
                current_index = i
                return
            i += 1
        current_var = -1
    elif search_mode == 1:
        i = global_vars.binary_search(0, len(global_vars)-1, name)
        if i > -1:
            current_var = global_vars[i]
            current_index = i
            return
        current_var = -1
    elif search_mode == 2:
        i = global_vars.interpolation_search(0, len(global_vars)-1, name)
        if i > -1:
            current_var = global_vars[i]
            current_index = i
            return
        current_var = -1


def set_var(name, value, readonly=False):
    search_for_var(name)
    if current_var != -1:
        current_var.value = value
        return current_var.value
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
    global current_var
    search_for_var(name)
    if current_var != -1:
        val = global_vars[current_index]
        del global_vars[current_index]
        return val
    PyscriptNameError(f"variable '{name}' was referenced before assignment", True)


def start_new_scope():
    cached.append(SortedList())
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
    if search_mode == 0:
        for var in cached[-1]:
            if var.name == name:
                var.value = removed.value
                return
    elif search_mode == 1:
        i = cached[-1].binary_search(0, len(cached[-1])-1, name)
        if i > -1:
            cached[-1][i].value = removed.value
    elif search_mode == 2:
        i = cached[-1].interpolation_search(0, len(cached[-1]) - 1, name)
        if i > -1:
            cached[-1][i].value = removed.value
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
