from tokens import calculate, parse, read
from vars import global_vars
from errors import *
import sys


filename = "print.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, "r+") as f:
    levels_to_ifs = {}
    condition = False
    prev_indentation = -1
    loop_lines = []
    indent_started = False
    loop_condition = False
    indentation_type = ""
    lines = []
    for line in f:
        lines.append(line)
    i = 0
    while i < len(lines):
        line = lines[i]
        tokenized, raw, count = read(line.strip("\n").strip())
        expanded = line.expandtabs().strip("\n")
        indentation = (len(expanded) - len(expanded.strip(" ")))//4
        if prev_indentation != -1:
            if prev_indentation != indentation - 1:
                if indent_started:
                    PyscriptSyntaxError("Invalid Syntax", True)
                else:
                    if indentation_type == "BRANCH":
                        prev_indentation = -1
                        condition = True
                    elif indentation_type == "WHILE":
                        if loop_condition:
                            prev_indentation = -1
                            i = loop_lines[-1]
                            line = lines[i]
                            tokenized, raw, count = read(line.strip("\n").strip())
                            expanded = line.expandtabs().strip("\n")
                            indentation = (len(expanded) - len(expanded.strip(" ")))//4
            indent_started = False
            if tokenized[0].type == "BRANCH":
                prev_indentation = indentation
            if indentation_type == "IF":
                if not condition:
                    continue
            elif indentation_type == "WHILE":
                if not loop_condition:
                    i += 1
                    continue

        if len(tokenized) == 0:
            i += 1
            continue

        if indentation not in levels_to_ifs.keys():
            parsed = parse(tokenized, raw, count)
        else:
            parsed = parse(tokenized, raw, count, levels_to_ifs[indentation])
        if type(parsed) == tuple:
            if type(parsed[0]) == bool:
                if parsed[1] == "BRANCH":
                    prev_indentation = indentation
                    condition = parsed
                    indent_started = True
                    levels_to_ifs[indentation] = condition
                    indentation_type = "IF"
                if parsed[1] == "WHILE":
                    prev_indentation = indentation
                    loop_condition = parsed[0]
                    if loop_condition:
                        if i not in loop_lines:
                            loop_lines.append(i)
                    else:
                        if i in loop_lines:
                            loop_lines.remove(i)
                            loop_condition = False
                    indent_started = True
                    indentation_type = "WHILE"

                i += 1
                continue
        calculate(parsed)
        i += 1

for var in global_vars:
    print(var)
