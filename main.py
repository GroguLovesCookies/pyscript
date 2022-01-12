from tokens import calculate, parse, read
from shared_vars import *
from vars import *
from labels import *
from errors import *
import sys
import time
from typing import List
from utility_classes.run_data import RunData
from token_def import TokDef
import os

FLAG_TERMINATE = "TERMINATE_LOOP"
FLAG_CONTINUE = "CONTINUE_ITER"


def find_chunk(line_i: int, file_lines: List[str]) -> List[str]:
    line_num: int = line_i
    chunk: List[str] = []
    prev_indentation_value: int = -1
    first_indentation_value: int = -1
    while line_num < len(file_lines):
        current_line: str = file_lines[line_num]
        expanded_line: str = current_line.expandtabs().strip("\n")
        indentation_value: int = (len(expanded_line) - len(expanded_line.strip(" "))) // 4
        if prev_indentation_value == -1:
            first_indentation_value = indentation_value
        else:
            if indentation_value == first_indentation_value:
                return chunk
            else:
                if indentation_value - prev_indentation_value >= 0:
                    chunk.append(current_line)
                elif indentation_value - prev_indentation_value < 0 and indentation_value <= first_indentation_value:
                    return chunk
                else:
                    chunk.append(current_line)
        line_num += 1
        prev_indentation_value = indentation_value
    return chunk


def run(lines: List[str], running_data: RunData = RunData.default, global_line: int = 0):
    looping: bool = running_data.looping
    original: bool = running_data.original
    i: int = 0
    new_global_line: int = global_line
    while i < len(lines):
        line: List[str] = lines[i]
        tokenized, raw, count = read(line.strip("\n").strip())

        if len(tokenized) == 0:
            i += 1
            new_global_line += 1
            continue
        if tokenized[0].val == "else":
            PyscriptSyntaxError("'else' without corresponding 'if'", True)
        parsed = parse(tokenized, raw, count)
        if type(parsed) == tuple:
            if type(parsed[0]) == bool:
                if parsed[1] == "BRANCH":
                    chunk_a: List[str] = find_chunk(i, lines)
                    if len(chunk_a) == 0:
                        PyscriptIndentationError("Unindented codeblock", True)
                    i += len(chunk_a) + 1
                    new_global_line += len(chunk_a) + 1
                    if i < len(lines):
                        line: str = lines[i]
                        tokenized, raw, count = read(line.strip("\n").strip())
                        if len(tokenized) > 0:
                            if tokenized[0].val == "else":
                                if len(tokenized) == 1:
                                    PyscriptSyntaxError("Missing colon at the end of 'else' statement", True)
                                if tokenized[-1].type != "COL_END":
                                    PyscriptSyntaxError("Missing colon at the end of 'else' statement", True)
                                chunk_b: List[str] = find_chunk(i, lines)
                                if len(chunk_b) == 0:
                                    PyscriptIndentationError("Unindented codeblock", True)
                            else:
                                chunk_b: str = ""
                        else:
                            chunk_b: str = ""
                    else:
                        chunk_b: str = ""
                    if parsed[0]:
                        val = run(chunk_a, running_data.set_attribute("original", False),
                                  global_line=new_global_line - (len(chunk_a) + 1))
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                        elif val == FLAG_CONTINUE:
                            return FLAG_CONTINUE
                        elif type(val) == tuple:
                            if val[0] == "jump":
                                new_global_line += val[1] - i
                                i = val[1]
                            elif val[0] == "return":
                                if original:
                                    return val[1]
                                else:
                                    return val
                            continue
                    else:
                        val = run(chunk_b, running_data.set_attribute("original", False), global_line=new_global_line)
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                        elif val == FLAG_CONTINUE:
                            return FLAG_CONTINUE
                        elif type(val) == tuple:
                            if not original:
                                return val
                            if val[0] == "jump":
                                new_global_line += val[1] - i
                                i = val[1]
                            elif val[0] == "return":
                                if original:
                                    return val[1]
                                else:
                                    return val
                            continue
                    i += 0 if len(chunk_b) == 0 else len(chunk_b) + 1
                    global_line += 0 if len(chunk_b) == 0 else len(chunk_b) + 1
                    continue
                elif parsed[1] == "WHILE":
                    loop_chunk: List[str] = find_chunk(i, lines)
                    if len(loop_chunk) == 0:
                        PyscriptIndentationError("Unindented codeblock", True)
                    line_a: int = i
                    if parsed[0]:
                        val = run(loop_chunk, running_data.set_attribute("looping", True)
                                  .set_attribute("original", False), global_line=new_global_line)
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                        if val == FLAG_CONTINUE:
                            new_global_line += line_a - i
                            i = line_a
                            continue
                        elif type(val) == list:
                            if val[0] == "jump":
                                new_global_line += val[1] - i
                                i = val[1]
                            elif val[0] == "return":
                                if original:
                                    return val[1]
                                else:
                                    return val
                        new_global_line += line_a - i
                        i = line_a
                    else:
                        i += len(loop_chunk) + 1
                        new_global_line += len(loop_chunk) + 1
                    continue
            elif parsed[0] is None:
                if parsed[1] == "continue":
                    if not looping:
                        PyscriptSyntaxError("'continue' statement outside of loop", True)
                    return FLAG_CONTINUE
                if parsed[1] == "break":
                    if not looping:
                        PyscriptSyntaxError("'break' statement outside of loop", True)
                    return FLAG_TERMINATE
                if parsed[1] == "jump":
                    if not original:
                        return "jump", parsed[2].line + 1
                if parsed[1] == "call":
                    run(parsed[2].chunk)
                    if type(val) == list:
                        if not original:
                            for var_name in parsed[2]:
                                remove_var(var_name)
                            return val
                        new_global_line += val[1] - i
                        i = val[1]
                        for var_name in parsed[2]:
                            remove_var(var_name)
                        continue
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "using":
                    using_chunk: List[str] = find_chunk(i, lines)
                    val = run(using_chunk, running_data.duplicate(), new_global_line)
                    if val == FLAG_CONTINUE:
                        for var_name in parsed[2]:
                            remove_var(var_name)
                        return FLAG_CONTINUE
                    elif val == FLAG_TERMINATE:
                        for var_name in parsed[2]:
                            remove_var(var_name)
                        return FLAG_TERMINATE
                    elif type(val) == list:
                        if val[0] == "jump":
                            new_global_line += val[1] - i
                            i = val[1]
                        elif val[0] == "return":
                            if original:
                                return val[1]
                            else:
                                return val
                    i += len(using_chunk) + 1
                    new_global_line += len(using_chunk) + 1
                    for var_name in parsed[2]:
                        remove_var(var_name)
                    continue
                if parsed[1] == "del":
                    for var_name in parsed[2]:
                        remove_var(var_name, True)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "local":
                    start_new_scope()
                    local_chunk = find_chunk(i, lines)
                    val = run(local_chunk)
                    if type(val) == list:
                        if val[0] == "jump":
                            new_global_line += val[1] - i
                            i = val[1]
                        elif val[0] == "return":
                            if original:
                                return val[1]
                            else:
                                return val
                    revert_from_scope()
                    i += len(local_chunk) + 1
                    new_global_line += len(local_chunk) + 1
                    continue
                if parsed[1] == "out":
                    for var_name in parsed[2]:
                        push_to_previous_cache(var_name)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "for":
                    for_chunk = find_chunk(i, lines)
                    condition = parsed[2]
                    update = parsed[3]
                    while True:
                        if len(condition) > 0:
                            temp_condition = condition[:]
                            continuation = calculate(parse(condition))
                            if not continuation:
                                i += len(for_chunk) + 1
                                new_global_line += len(for_chunk) + 1
                                break
                            condition = temp_condition[:]
                        val = run(for_chunk,
                                  running_data.set_attribute("looping", True).set_attribute("original", False),
                                  new_global_line)
                        if val == FLAG_TERMINATE:
                            i += len(for_chunk) + 1
                            new_global_line += len(for_chunk) + 1
                            break
                        elif val == FLAG_CONTINUE:
                            for i, update_expr in enumerate(update):
                                temp = update_expr[:]
                                calculate(parse(update_expr))
                                update[i] = temp[:]
                            continue
                        elif type(val) == list:
                            if val[0] == "jump":
                                new_global_line += val[1] - i
                                i = val[1]
                            elif val[0] == "return":
                                if original:
                                    return val[1]
                                else:
                                    return val
                        for index, update_expr in enumerate(update):
                            temp = update_expr[:]
                            calculate(parse(update_expr))
                            update[index] = temp[:]
                    continue
                if parsed[1] == "func":
                    variable = get_var(parsed[2].name)
                    variable.extra_args = [find_chunk(i, lines), parsed[4], *parsed[3]]
                    variable.value = variable
                    variable.run_func = run
                    i += len(variable.extra_args[0]) + 1
                    new_global_line += len(variable.extra_args[0]) + 1
                    continue
                if parsed[1] == "extern":
                    if os.path.splitext(parsed[4])[1] != ".py":
                        PyscriptSyntaxError("Extern functions must include .py extension", True)
                    if os.path.exists(os.path.join("pyscript/", parsed[4])):
                        with open(os.path.join("pyscript/", parsed[4])) as file:
                            py_program = file.read().split("\n")
                            for j, py_line in enumerate(py_program):
                                if py_line.startswith("def"):
                                    name = read(py_line)[1][1]
                                    if name.val == parsed[2]:
                                        chunk = find_chunk(j, py_program)
                                        for k, line in enumerate(chunk):
                                            chunk[k] = line.strip(" ").strip("\t")
                                        if parsed[5] is None:
                                            create_var(name.val, 0, [True, True, False], True, [chunk, *parsed[3]], exec)
                                        else:
                                            create_var(name.val, 0, [True, True, False], True, [chunk, *parsed[3]], exec,
                                                       parsed[5][0].val)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "return":
                    if not original:
                        return "return", parsed[2]
                    else:
                        return parsed[2]
                if parsed[1] == "import":
                    if os.path.exists("pyscript/" + parsed[2]):
                        with open("pyscript/" + parsed[2]) as lib:
                            if type(parsed[4]) == list:
                                with Scope():
                                    with SetReset("__name__", "__import__"):
                                        with open(default_configurations, "r") as config:
                                            for library in config.readlines():
                                                run([f"import * from {library}"])
                                        run(lib.read().split("\n"))
                                        additional_vars = global_vars.__copy__()
                                        if len(parsed[4]) == 0:
                                            if parsed[3] == "":
                                                lib_name = os.path.split(os.path.splitext(parsed[2])[0])[-1]
                                            else:
                                                lib_name = parsed[3]
                                            if lib_name in un_ops:
                                                un_ops.remove(lib_name)

                                            var_import_index = 0
                                            while var_import_index < len(global_vars):
                                                var = global_vars[var_import_index]
                                                if var.name in un_ops:
                                                    un_ops.remove(var.name)
                                                if var.name in funcs:
                                                    funcs.remove(var.name)
                                                if var.readonly[2] and var.name != "__name__":
                                                    del global_vars[var_import_index]
                                                    var_import_index -= 1
                                                var_import_index += 1
                                with open(default_configurations, "r") as config:
                                    for library in config.readlines():
                                        run([f"import * from {library}"])
                                set_var("__name__", "__main__", [True, True, True])
                            else:
                                with SetReset("__name__", "__import__"):
                                    run(lib.read().split("\n"))
                                    var_import_index = 0
                                    while var_import_index < len(global_vars):
                                        var = global_vars[var_import_index]
                                        if var.readonly[2]:
                                            del global_vars[var_import_index]
                                            var_import_index -= 1
                                        var_import_index += 1

                            if type(parsed[4]) == list:
                                if len(parsed[4]) == 0:
                                    create_var(lib_name, 0, [True, True, False], extra_args=additional_vars)
                                else:
                                    for name in parsed[4]:
                                        fetched = additional_vars[additional_vars
                                                                  .interpolation_search(0, len(additional_vars) - 1,
                                                                                        name)]
                                        if not fetched.readonly[2]:
                                            create_var(fetched.name, fetched.value, fetched.readonly, fetched.is_callable,
                                                       fetched.extra_args, fetched.run_func, fetched.r_value)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "switch":
                    switch_chunk = find_chunk(i, lines)
                    tokenized_switch_chunk = [read(switch_line.strip("\n"))[0] for switch_line in switch_chunk]
                    case_i = 0
                    found = False
                    found_chunk = []
                    while case_i < len(tokenized_switch_chunk) and not found:
                        if tokenized_switch_chunk[case_i][0].val != "case":
                            PyscriptSyntaxError("Invalid Syntax", True)
                        if parse(tokenized_switch_chunk[case_i])[2] == parsed[2]:
                            found = True
                            case_i += 1
                            while case_i < len(tokenized_switch_chunk) and \
                                    tokenized_switch_chunk[case_i][0].val != "case":
                                found_chunk.append(switch_chunk[case_i])
                                case_i += 1
                            if len(found_chunk) == 0:
                                PyscriptSyntaxError("Invalid Syntax", True)
                            continue
                        case_i += 1
                        while case_i < len(tokenized_switch_chunk) and \
                                tokenized_switch_chunk[case_i][0].val != "case":
                            case_i += 1
                    val = run(found_chunk)
                    if type(val) == list:
                        if val[0] == "jump":
                            new_global_line += val[1] - i
                            i = val[1]
                        elif val[0] == "return":
                            if original:
                                return val[1]
                            else:
                                return val
                    i += len(switch_chunk) + 1
                    new_global_line += len(switch_chunk) + 1
                    continue

        elif type(parsed) == Label:
            parsed.line = new_global_line
            parsed.chunk = find_chunk(i, lines)
            # print(Label.all_labels) # Debug
            if not parsed.is_def_label:
                run(parsed.chunk, global_line=new_global_line + 1)
            i += len(parsed.chunk) + 1
            new_global_line += len(parsed.chunk) + 1
            continue
        elif type(parsed) == TokDef:
            i += 1
            new_global_line += 1
            continue
        calculate(parsed)
        i += 1
        new_global_line += 1


filename: str = "math_test.pyscript"
default_configurations: str = "defaults.txt"
timing: bool = False
if len(sys.argv) > 1:
    filename: str = sys.argv[1]
if len(sys.argv) > 2:
    if sys.argv[2] == "timed":
        timing = True
    if not timing:
        print("Could not recognise command")
        sys.exit(1)


with open("pyscript/" + filename, "r+") as f:
    program: List[str] = []
    for l in f:
        program.append(l)
    if timing:
        start_time = time.time()
        run(program, RunData(False, True))
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time}")
    else:
        set_var("__name__", "__main__", [True, True, True])
        with open(default_configurations, "r") as config:
            for library in config.readlines():
                run([f"import * from {library}"])
        run(program, RunData(False, True))
