from tokens import calculate, parse, read
from vars import global_vars


with open("print.pyscript", newline="") as f:
    for line in f:
        tokenized, raw, count = read(line)
        print(parse(tokenized))