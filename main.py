from tokens import calculate, parse, read
from vars import global_vars
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


def run(lines, looping=False):
    i = 0
    while i < len(lines):
        line = lines[i]
        tokenized, raw, count = read(line.strip("\n").strip())

        if len(tokenized) == 0:
            i += 1
            continue
        parsed = parse(tokenized, raw, count)
        if type(parsed) == tuple:
            if type(parsed[0]) == bool:
                if parsed[1] == "BRANCH":
                    chunk_a = find_chunk(i, lines)
                    line_a = i
                    i += len(chunk_a)
                    line = lines[i]
                    tokenized, raw, count = read(line.strip("\n").strip())
                    if tokenized[0].val == "else":
                        line_b = i
                        chunk_b = find_chunk(i, lines)
                    else:
                        line_b = line_a
                        chunk_b = ""
                    if parsed[0]:
                        if run(chunk_a, looping) == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                    else:
                        if run(chunk_b, looping) == FLAG_TERMINATE:
                            return FLAG_TERMINATE
                    chunk_to_use = chunk_b if line_b != line_a else chunk_a
                    i += len(chunk_to_use) - (len(chunk_to_use)-1)
                    continue
                elif parsed[1] == "WHILE":
                    loop_chunk = find_chunk(i, lines)
                    line_a = i
                    if parsed[0]:
                        if run(loop_chunk, True) == FLAG_TERMINATE:
                            i += len(loop_chunk) + 1
                            continue
                        i = line_a
                    else:
                        i += len(loop_chunk) + 1
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
        elif type(parsed) == Label:
            parsed.line = i
            parsed.chunk = find_chunk(i, lines)
            # print(Label.all_labels)
            i += len(parsed.chunk) + 1
            run(parsed.chunk)
            continue
        calculate(parsed)
        i += 1


filename = "branch.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, "r+") as f:
    program = []
    for l in f:
        program.append(l)
    run(program)

for var in global_vars:
    print(var)
