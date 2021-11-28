from errors import PyscriptNameError, PyscriptSyntaxError
from structures.sorted_list import SortedList
from utility_classes.run_data import RunData
from inliner import make_inline
from shared_vars import *


global_vars = SortedList()
cached = []
current_scope_pointer = -1
current_var = None
current_index = -1
running_function = False
new_vars = []
func_to_register = lambda a: a
# 0: linear, 1: binary, 2: interpolation
search_mode = 0


class Scope:
    def __enter__(self):
        start_new_scope()

    def __exit__(self, exc_type, exc_val, exc_tb):
        revert_from_scope()


class SetReset:
    def __init__(self, name, value):
        var = get_var(name)
        if var != -1:
            self.original = get_var(name).value
        else:
            self.original = None
        self.name = name
        self.value = value

    def __enter__(self):
        set_var(self.name, self.value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original is not None:
            set_var(self.name, self.original)
        else:
            remove_var(self.name)


class Variable:
    def __init__(self, name, value, readonly=False, is_callable=False, extra_args=None, run_func=None, r_value=None):
        if extra_args is None:
            extra_args = []
        self.value = value
        self.name = name
        self.readonly = readonly
        self.is_callable = is_callable
        self.extra_args = extra_args
        self.run_func = run_func
        self.r_value = r_value
        self.name_val = 0
        self.container = False
        for letter in self.name:
            self.name_val += ord(letter)
        if self.container:
            for arg in extra_args:
                self.__setattr__(arg.name, arg)

    def __repr__(self):
        if not self.is_callable:
            value = self.value
            if type(self.value) == str:
                value = f"\"{self.value}\""
            if not self.readonly:
                return f"{self.name} = {value}"
            else:
                return f"readonly {self.name} = {value}"
        return f"'function {self.name}'"

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
        global running_function, new_vars
        if not self.is_callable:
            PyscriptSyntaxError(f"Variable {self.name} is not callable", True)
        cached.insert(0, SortedList())
        if self.run_func != exec:
            running_function = True
            new_vars.clear()
            for var, value in kwargs.items():
                set_var(var, value, [False, False])
            r_value = self.run_func(self.extra_args[0], RunData.default.set_attribute("original", True))
            mix_scopes()
            running_function = False
            return r_value
        else:
            for var, value in kwargs.items():
                str_to_run = self.extra_args[0][:]
                if type(value) != str:
                    str_to_run.insert(0, f'{var} = {value}')
                else:
                    str_to_run.insert(0, f'{var} = "{value}"')
                loc = {}
                self.run_func(";".join(str_to_run), globals(), loc)
                mix_scopes()
                if self.r_value is not None:
                    if self.r_value in loc.keys():
                        return loc[self.r_value]
                    PyscriptNameError(f"Expected variable named {self.r_value}, var not found.", True)

    def get_inline_form(self, kwargs, read):
        str_to_make_inline = self.extra_args[0][:]
        for var, value in kwargs.items():
            str_to_make_inline.insert(0, f"{var}={value}")
            tokenized_chunk = [read(line)[1] for line in str_to_make_inline]
        return make_inline(tokenized_chunk)

    def pyscript_var_assign(self, other):
        other.value = self.value
        other.is_callable = self.is_callable
        other.extra_args = self.extra_args
        other.run_func = self.run_func
        other.r_value = self.r_value
        un_ops.add(other.name)
        funcs.add(other.name)

    def pyscript_var_deassign(self, other):
        other.is_callable = False
        other.extra_args = []
        other.run_func = None
        other.r_value = None
        un_ops.remove(other.name)
        funcs.remove(other.name)

    def pyscript_var_delete(self, other):
        un_ops.remove(other.name)
        funcs.remove(other.name)


def create_var(name, value, readonly=None, is_callable=False, extra_args=None, run_func=None, r_value=None):
    if readonly is None:
        readonly = [False, False]
    if extra_args is None:
        extra_args = []
    var = Variable(name, value, readonly, is_callable, extra_args, run_func, r_value)
    if 'pyscript_var_assign' in dir(value):
        value.pyscript_var_assign(var)
    global_vars.append(var)
    return var.value, var


def get_var(name) -> Variable:
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


def set_var(name, value, readonly=None):
    if readonly is None:
        readonly = [False, False]
    search_for_var(name)
    if not running_function:
        if current_var != -1:
            if 'pyscript_var_deassign' in dir(current_var.value):
                current_var.value.pyscript_var_deassign(current_var)
    if 'pyscript_var_assign' in dir(value):
        if current_var != -1:
            value.pyscript_var_assign(current_var)
            if running_function:
                push_to_previous_cache(current_var.name)
            return current_var.value, current_var
        var = create_var(name, 0, readonly)[1]
        value.pyscript_var_assign(var)
        return var.value, var
    else:
        if current_var != -1:
            current_var.value = value
            if running_function:
                push_to_previous_cache(current_var.name)
            return current_var.value, current_var
        new_vars.append(name)
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


def mix_scopes():
    for var in global_vars:
        if var.name not in new_vars:
            push_to_previous_cache(var.name)
    revert_from_scope()


def remove_var(name, user_delete=False):
    global current_var
    search_for_var(name)
    if current_var != -1:
        if user_delete and 'pyscript_var_delete' in dir(current_var.value):
            current_var.value.pyscript_var_delete(current_var)
        if user_delete and current_var.readonly[1]:
            PyscriptSyntaxError(f"Attempting to delete indestructible variable '{name}'", True)
        val = global_vars[current_index]
        del global_vars[current_index]
        return val
    PyscriptNameError(f"variable '{name}' was referenced before assignment", True)


def start_new_scope():
    cached.append(SortedList())
    for var in global_vars:
        cached[-1].append(Variable(var.name, var.value, var.readonly, var.is_callable, var.extra_args, var.run_func,
                                   var.r_value))
    global_vars.clear()


def revert_from_scope():
    global global_vars
    global_vars.clear()
    for var in cached[-1]:
        create_var(var.name, var.value, var.readonly, var.is_callable, var.extra_args, var.run_func, var.r_value)
    del cached[-1]


def push_to_previous_cache(name, destructive=False):
    removed = remove_var(name)
    if not destructive:
        create_var(removed.name, removed.value, removed.readonly, removed.is_callable, removed.extra_args, removed.run_func,
                   removed.r_value)
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
