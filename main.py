from tokens import calculate, parse, read, prep_unary, bracketize, unwrap_unary
from vars import global_vars


with open("bools.pyscript", newline="") as f:
    for line in f:
        tokenized, raw, count = read(line.strip("\n").strip())

        if len(tokenized) == 0:
            continue

        calculate(parse(tokenized, raw, count))

for var in global_vars:
    print(var)