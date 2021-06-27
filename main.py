from tokens import calculate, parse, read
from vars import global_vars
import sys


filename = "print.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, newline="") as f:
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
                    print("SyntaxError: Unexpected Indent")
                    sys.exit(1)
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

        parsed = parse(tokenized, raw, count)
        if type(parsed) == bool:
            prev_indentation = indentation
            condition = parsed
            branch_started = True
            continue
        calculate(parsed)

for var in global_vars:
    print(var)
