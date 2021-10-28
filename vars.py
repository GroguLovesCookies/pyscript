from errors import PyscriptNameError, PyscriptSyntaxError
from structures.sorted_list import SortedList
from utility_classes.run_data import RunData
import time


global_vars = SortedList()
cached = []
current_scope_pointer = -1
current_var = None
current_index = -1
# 0: linear, 1: binary, 2: interpolation
search_mode = 0


class Variable:
    def __init__(self, name, value, readonly=False, is_callable=False, extra_args=None, run_func=None):
        if extra_args is None:
            extra_args = []
        self.value = value
        self.name = name
        self.readonly = readonly
        self.is_callable = is_callable
        self.extra_args = extra_args
        self.run_func = run_func
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
            op_val = other.name
        if type(other) == str:
            op_val = other
        if len(op_val) > len(self.name):
            return ord(op_val[len(self.name)])
        elif len(op_val) < len(self.name):
            return -ord(self.name[len(op_val)])
        else:
            for i, letter in enumerate(op_val):
                if letter != self.name[i]:
                    return ord(self.name[i])-ord(letter)
            return 0

    def __mul__(self, other):
        if type(other) == Variable:
            op_val = other.name_val
        elif type(other) == str:
            op_val = 0
            for letter in other:
                op_val += ord(letter)
        return self.name_val * op_val

    def run(self, kwargs):
        if not self.is_callable:
            PyscriptSyntaxError(f"Variable {self.name} is not callable", True)
        start_new_scope()
        if self.run_func != exec:
            for var, value in kwargs.items():
                create_var(var, value, False)
            r_value = self.run_func(self.extra_args[0], RunData.default.set_attribute("original", True))
            revert_from_scope()
            return r_value
        else:
            for var, value in kwargs.items():
                if type(value) != str:
                    self.extra_args[0].insert(0, f'{var} = {value}')
                else:
                    self.extra_args[0].insert(0, f'{var} = "{value}"')
                self.run_func(";".join(self.extra_args[0]))
                revert_from_scope()


def create_var(name, value, readonly=False, is_callable=False, extra_args=None, run_func=None):
    if extra_args is None:
        extra_args = []
    var = Variable(name, value, readonly, is_callable, extra_args, run_func)
    global_vars.append(var)
    return var.value, var


def get_var(name):
    search_for_var(name)
    return current_var


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
        cached[-1].append(Variable(var.name, var.value, var.readonly, var.is_callable, var.extra_args, var.run_func))
    global_vars.clear()


def revert_from_scope():
    global global_vars
    global_vars.clear()
    for var in cached[-1]:
        create_var(var.name, var.value, var.readonly, var.is_callable, var.extra_args, var.run_func)
    del cached[-1]


def push_to_previous_cache(name):
    removed = remove_var(name)
    create_var(removed.name, removed.value, removed.readonly, removed.is_callable, removed.extra_args, removed.run_func)
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
