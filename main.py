from tokens import calculate, parse, read
from vars import global_vars
from errors import *
import sys


filename = "print.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, newline="") as f:
    levels_to_ifs = {}
    condition = False
    prev_indentation = -1
    branch_started = False
    for line in f:
        tokenized, raw, count = read(line.strip("\n").strip())
        expanded = line.expandtabs().strip("\n")
        indentation = (len(expanded) - len(expanded.strip(" ")))//4
        if prev_indentation != -1:
            if prev_indentation != indentation - 1:
                if branch_started:
                    PyscriptSyntaxError("Invalid Syntax", True)
                else:
                    prev_indentation = -1
                    condition = True
            branch_started = False
            if tokenized[0].type == "BRANCH":
                prev_indentation = indentation
            if not condition:
                continue

        if len(tokenized) == 0:
            continue

        if indentation not in levels_to_ifs.keys():
            parsed = parse(tokenized, raw, count)
        else:
            parsed = parse(tokenized, raw, count, levels_to_ifs[indentation])
        if type(parsed) == bool:
            prev_indentation = indentation
            condition = parsed
            branch_started = True
            levels_to_ifs[indentation] = condition
            continue
        calculate(parsed)

for var in global_vars:
    print(var)
