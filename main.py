from tokens import calculate, parse, read
from vars import *
from labels import *
from errors import *
import sys
import time
from typing import List
from utility_classes.run_data import RunData

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


def run(lines: List[str], running_data: RunData = RunData.default, global_line: int = 0, is_loop: bool = False):
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
                            if not original:
                                return val
                            new_global_line += val[1] - i
                            i = val[1]
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
                            new_global_line += val[1] - i
                            i = val[1]
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
                            if not original:
                                return val
                            new_global_line += val[1] - i
                            i = val[1]
                            continue
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
                        if not original:
                            for var_name in parsed[2]:
                                remove_var(var_name)
                            return val
                        new_global_line += val[1] - i
                        i = val[1]
                        for var_name in parsed[2]:
                            remove_var(var_name)
                        continue
                    i += len(using_chunk) + 1
                    new_global_line += len(using_chunk) + 1
                    for var_name in parsed[2]:
                        remove_var(var_name)
                    continue
                if parsed[1] == "del":
                    for var_name in parsed[2]:
                        remove_var(var_name)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "local":
                    start_new_scope()
                    local_chunk = find_chunk(i, lines)
                    val = run(local_chunk)
                    if type(val) == list:
                        if not original:
                            revert_from_scope()
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
                        for index, update_expr in enumerate(update):
                            temp = update_expr[:]
                            calculate(parse(update_expr))
                            update[index] = temp[:]
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
        calculate(parsed)
        i += 1
        new_global_line += 1


filename: str = "print.pyscript"
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
        run(program, RunData(False, True))

for var in global_vars:
    print(var)
