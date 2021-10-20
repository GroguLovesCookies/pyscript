from tokens import calculate, parse, read
from vars import global_vars, remove_var
from labels import *
from errors import *
import sys
import time
from typing import List


FLAG_TERMINATE = "TERMINATE_LOOP"


def find_chunk(line_i: int, file_lines: List[str]) -> List[str]:
    line_num: int = line_i
    chunk: List[str] = []
    prev_indentation_value: int = -1
    first_indentation_value: int = -1
    while line_num < len(file_lines):
        current_line: str = file_lines[line_num]
        expanded_line: str = current_line.expandtabs().strip("\n")
        indentation_value: int = (len(expanded_line) - len(expanded_line.strip(" ")))//4
        if prev_indentation_value == -1:
            first_indentation_value = indentation_value
        else:
            if indentation_value == first_indentation_value:
                return chunk
            else:
                if indentation_value-prev_indentation_value >= 0:
                    chunk.append(current_line)
                elif indentation_value-prev_indentation_value < 0 and indentation_value <= first_indentation_value:
                    return chunk
                else:
                    chunk.append(current_line)
        line_num += 1
        prev_indentation_value = indentation_value
    return chunk


def run(lines: List[str], looping: bool = False, original: bool = False, global_line: int = 0):
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
                    i += len(chunk_a)+1
                    new_global_line += len(chunk_a)+1
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
                        val = run(chunk_a, looping, global_line=new_global_line-(len(chunk_a)+1))
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                        elif type(val) == tuple:
                            if not original:
                                return val
                            new_global_line += val[1] - i
                            i = val[1]
                            continue
                    else:
                        val = run(chunk_b, looping, global_line=new_global_line)
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                        elif type(val) == tuple:
                            if not original:
                                return val
                            new_global_line += val[1] - i
                            i = val[1]
                            continue
                    i += 0 if len(chunk_b) == 0 else len(chunk_b)+1
                    global_line += 0 if len(chunk_b) == 0 else len(chunk_b)+1
                    continue
                elif parsed[1] == "WHILE":
                    loop_chunk: List[str] = find_chunk(i, lines)
                    if len(loop_chunk) == 0:
                        PyscriptIndentationError("Unindented codeblock", True)
                    line_a: int = i
                    if parsed[0]:
                        val = run(loop_chunk, True, global_line=new_global_line)
                        if val == FLAG_TERMINATE:
                            return FLAG_TERMINATE
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
                        new_global_line += len(loop_chunk)+1
                    continue
            elif parsed[0] is None:
                if parsed[1] == "continue":
                    if not looping:
                        PyscriptSyntaxError("'continue' statement outside of loop", True)
                    return
                if parsed[1] == "break":
                    if not looping:
                        PyscriptSyntaxError("'break' statement outside of loop", True)
                    return FLAG_TERMINATE
                if parsed[1] == "jump":
                    if not original:
                        return "jump", parsed[2].line+1
                if parsed[1] == "call":
                    run(parsed[2].chunk)
                    i += 1
                    new_global_line += 1
                    continue
                if parsed[1] == "using":
                    using_chunk: List[str] = find_chunk(i, lines)
                    run(using_chunk, looping=looping)
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
        elif type(parsed) == Label:
            parsed.line = new_global_line
            parsed.chunk = find_chunk(i, lines)
            # print(Label.all_labels) # Debug
            if not parsed.is_def_label:
                run(parsed.chunk, global_line=new_global_line+1)
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
        run(program, original=True)
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time}")
    else:
        run(program, original=True)


for var in global_vars:
    print(var)
