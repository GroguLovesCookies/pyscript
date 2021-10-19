from tokens import calculate, parse, read
from vars import global_vars, remove_var
from labels import *
from errors import *
import sys


FLAG_TERMINATE = "TERMINATE_LOOP"


def find_chunk(line_i, file_lines):
    line_num = line_i
    chunk = []
    prev_indentation_value = -1
    first_indentation_value = -1
    while line_num < len(file_lines):
        current_line = file_lines[line_num]
        expanded_line = current_line.expandtabs().strip("\n")
        indentation_value = (len(expanded_line) - len(expanded_line.strip(" ")))//4
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


def run(lines, looping=False, original=False, global_line=0):
    i = 0
    new_global_line = global_line
    while i < len(lines):
        line = lines[i]
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
                    chunk_a = find_chunk(i, lines)
                    if len(chunk_a) == 0:
                        PyscriptIndentationError("Unindented codeblock", True)
                    i += len(chunk_a)+1
                    new_global_line += len(chunk_a)+1
                    if i < len(lines):
                        line = lines[i]
                        tokenized, raw, count = read(line.strip("\n").strip())
                        if len(tokenized) > 0:
                            if tokenized[0].val == "else":
                                if len(tokenized) == 1:
                                    PyscriptSyntaxError("Missing colon at the end of 'else' statement", True)
                                if tokenized[-1].type != "COL_END":
                                    PyscriptSyntaxError("Missing colon at the end of 'else' statement", True)
                                chunk_b = find_chunk(i, lines)
                                if len(chunk_b) == 0:
                                    PyscriptIndentationError("Unindented codeblock", True)
                            else:
                                chunk_b = ""
                        else:
                            chunk_b = ""
                    else:
                        chunk_b = ""
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
                    loop_chunk = find_chunk(i, lines)
                    if len(loop_chunk) == 0:
                        PyscriptIndentationError("Unindented codeblock", True)
                    line_a = i
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
                    using_chunk = find_chunk(i, lines)
                    run(using_chunk, looping=looping)
                    i += len(using_chunk) + 1
                    new_global_line += len(using_chunk) + 1
                    for var_name in parsed[2]:
                        remove_var(var_name)
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


filename = "print.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, "r+") as f:
    program = []
    for l in f:
        program.append(l)
    run(program, original=True)

for var in global_vars:
    print(var)
