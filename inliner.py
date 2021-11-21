import tokens
import errors


def is_assignment(line):
    return "EQUALS" in [tok.val for tok in line]


def is_return(line):
    return line_starts_with("return", line)


def is_inline(chunk):
    for i, line in enumerate(chunk):
        if i == len(chunk) - 1:
            if not is_return(line):
                return False
        else:
            if not is_assignment(line):
                return False
    return True


def line_starts_with(val, line):
    return len(line) > 0 and line[0].val == val


def find_starts_with(val, chunk, criterion=lambda a: True):
    for line in chunk:
        if line_starts_with(val, line) and criterion(line):
            return line
    errors.PyscriptSyntaxError("Invalid Syntax", True)


def substitute(chunk, line):
    new_line = line[:]
    inserted_tokens = 0
    for i, tok in enumerate(line):
        if tok.pseudo_type == "REFERENCING":
            found_line = tokens.split_list_by_token("EQUALS", "EQUALS",
                                                    find_starts_with(tok.val, chunk, is_assignment))[-1]

            bracketized: List[tokens.Token] = tokens.prep_unary(found_line)
            bracketized, unused = tokens.bracketize(bracketized)
            bracketized = tokens.unwrap_unary(bracketized)

            val = substitute(chunk, bracketized)
            del new_line[i+inserted_tokens]
            for token in reversed(val):
                new_line.insert(i+inserted_tokens, token)
            inserted_tokens += len(val) - 1
    return new_line


def make_inline(chunk):
    if is_inline(chunk):
        return_line = chunk[-1]

        substituted = substitute(chunk, return_line)
        substituted = substituted[1:]
        bracketized: List[tokens.Token] = tokens.prep_unary(substituted)
        bracketized, unused = tokens.bracketize(bracketized)
        bracketized = tokens.unwrap_unary(bracketized)
        return bracketized
    errors.PyscriptSyntaxError("Invalid Format For Inline Function")
