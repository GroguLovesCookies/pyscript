from tokens import calculate, parse, read
from vars import global_vars
import sys


filename = "print.pyscript"
if len(sys.argv) > 1:
    filename = sys.argv[1]


with open("pyscript/" + filename, newline="") as f:
    for line in f:
        tokenized, raw, count = read(line.strip("\n").strip())

        if len(tokenized) == 0:
            continue

        calculate(parse(tokenized, raw, count))

for var in global_vars:
    print(var)
