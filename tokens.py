# Imports
from errors import *
from vars import set_var, global_vars, index_set_var
from nodes import *
from range import range_from_to

# Define tokens
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POWER = "POWER"
TT_MODULO = "MOD"
TT_RANGE_TO = "RANGE_TO"
TT_RANGE_THROUGH = "RANGE_THROUGH"
TT_GREATER = "GREATER_THAN"
TT_LESS = "LESS_THAN"
TT_IS_EQUAL = "IS_EQUAL"
TT_NOT_EQUAL = "NOT_EQUAL"
TT_GREATER_EQUAL = "GREATER_EQUAL"
TT_LESS_EQUAL = "LESS_EQUAL"
TT_RPAREN = "RPAREN"
TT_LPAREN = "LPAREN"
TT_BRACKET = "BRACKET"
TT_INT = "INT"
TT_STR = "STR"
TT_FLOAT = "FLOAT"
TT_BOOL = "BOOL"
TT_LIST = "LIST"
TT_VAR = "VAR"
TT_EQUALS = "EQUALS"
TT_KEYWORD = "KW"
TT_UNIT = "DUMMY"
TT_BRANCH = "BRANCH"
TT_INDEX = "INDEX"
TT_WHILE = "WHILE"

# Define pseudo-types
PT_ASSIGNMENT = "ASSIGNING"
PT_REFERENCE = "REFERNCING"
PT_INDEX_ASSIGNMENT = "INDEX_ASSIGN"
PT_INDEX_REFERENCE = "INDEX_REFERENCE"

# Define keywords
KW_READONLY = "readonly"
KW_TRUE = "True"
KW_FALSE = "False"
KW_AND = "and"
KW_OR = "or"
KW_XOR = "xor"
KW_NOT = "not"
KW_IF = "if"
KW_ELSE = "else"
KW_WHILE = "while"
KW_CONTINUE = "continue"
KEYWORDS = {KW_READONLY: TT_KEYWORD, KW_TRUE: TT_BOOL, KW_FALSE: TT_BOOL, KW_AND: None, KW_OR: None, KW_XOR: None,
            KW_NOT: None, KW_IF: TT_BRANCH, KW_ELSE: TT_BRANCH, KW_WHILE: TT_WHILE, KW_CONTINUE: TT_KEYWORD}

# Define types
types = [TT_INT, TT_FLOAT, TT_STR, TT_LIST, TT_BOOL]

# Define unary operators
un_ops = [KW_NOT]

# Define operator list
op_chars = ["+", "-", "*", "/", "^", "%", "=", ">", "<", "!", ":"]

# Define indexed versions of un-indexed pseudo-types
indexed = {PT_ASSIGNMENT: PT_INDEX_ASSIGNMENT, PT_REFERENCE: PT_INDEX_REFERENCE,
           PT_INDEX_ASSIGNMENT: PT_INDEX_ASSIGNMENT, PT_INDEX_REFERENCE: PT_INDEX_REFERENCE}


# Class Token
class Token:
    """A class to define properties of tokens used by the lexer"""

    def __init__(self, tok_type, val):
        self.val = val
        self.type = tok_type
        self.pseudo_type = None
        self.extra_params = []

    def __repr__(self):
        if self.type is None:
            return self.val
        return f"{self.type}:{self.val}"


def prep_unary(tokenized):
    start_index_stack = []
    i = 0
    start_index = -1
    insert_number = 0
    while i < len(tokenized):
        token = tokenized[i]
        if token.val == KW_NOT:
            if start_index < 0:
                start_index = i
        else:
            if token.val == TT_LPAREN:
                start_index_stack.append(start_index)
                start_index = -1
            elif token.val == TT_RPAREN:
                start_index = start_index_stack.pop()
            elif start_index >= 0:
                change = insert_number
                if insert_number > 0:
                    change = insert_number-1
                thing = tokenized[start_index: i + 1 - change]
                del tokenized[start_index: i - change]
                i -= len(thing) - 1
                tokenized[start_index] = Token(TT_UNIT, thing)
                insert_number += 1
                start_index = -1
        i += 1
    return tokenized


def unwrap_unary(tokenized):
    i = 0
    while i < len(tokenized):
        token = tokenized[i]
        if token.type == TT_UNIT:
            del tokenized[i]
            tokenized.insert(i, Token(TT_BRACKET, TT_RPAREN))
            for item in reversed(bracketize(token.val, True)[0]):
                tokenized.insert(i, item)
            tokenized.insert(i, Token(TT_BRACKET, TT_LPAREN))
        i += 1
    return tokenized


def split_list(text, character=" ", strip=False):
    splitted = []
    quote_ignore = False
    bracket_ignore = False
    current = ""

    for char in text:
        if char == "\"":
            quote_ignore = not quote_ignore
            current += char
        elif char == "[":
            bracket_ignore = True
            current += char
        elif char == "]":
            bracket_ignore = False
            current += char
        elif char == character:
            if not quote_ignore and not bracket_ignore:
                splitted.append(current if not strip else current.strip())
                current = ""
            else:
                current += char
        else:
            current += char

    if current != "":
        splitted.append(current if not strip else current.strip())

    return splitted


def get_list(text, i):
    listed = read(text_extract(text[i:], opening="[", closing="]"), ignore_exception=True, group_by=",")
    i = get_closing_text(text[i:], "[", "]") + i
    j = 0
    while j < len(listed):
        listed[j] = calculate(parse(listed[j]))
        j += 1
    return Token(TT_LIST, listed)


# Reading function
def read(text, ignore_exception=False, group_by=""):
    """A function to tokenize input text"""

    if group_by != "":
        results = [read(item)[0] for item in split_list(text, ",", True)]
        return results
    else:
        # Set initial state
        tokens = []
        i = 0
        multiplier = 1
        latest = None

        # Read loop
        while True:
            # If at the end of list, make sure of correct
            # syntax, add implicit bracketing, and return
            if i >= len(list(text)):
                if not ignore_exception:
                    analyse_tokens(tokens)
                raw = tokens[:]
                tokens = prep_unary(tokens)
                tokens, count = bracketize(tokens)
                tokens = unwrap_unary(tokens)
                assign_pseudo_types(tokens)
                assign_pseudo_types(raw)
                tokens = remove_index_tokens(tokens)
                raw = remove_index_tokens(raw)
                return tokens, raw, count

            # Analyse character
            char = text[i]

            # Operator checks
            if char in op_chars:
                op = ""
                while char in op_chars:
                    op += char
                    i += 1
                    if i < len(text):
                        char = text[i]
                    else:
                        break
                if op == "+":
                    tokens.append(Token(None, TT_PLUS))
                elif op == "-":
                    # If the "-" sign is at beginning (i = 0), it
                    # is a negative sign, not operator
                    if i == 0:
                        multiplier = -1

                    # If the latest is an operator or an opening
                    # bracket, it is a negative sign, not operator
                    elif latest.type is None or latest.val == TT_LPAREN or latest.type == TT_EQUALS:
                        multiplier = -1

                    # If you get here, it is an operator
                    else:
                        tokens.append(Token(None, TT_MINUS))
                elif op == "--":
                    tokens.append(Token(None, TT_MINUS))
                    multiplier = -1
                elif op == "*":
                    tokens.append(Token(None, TT_MUL))
                elif op == "/":
                    tokens.append(Token(None, TT_DIV))
                elif op == "^":
                    tokens.append(Token(None, TT_POWER))
                elif op == "%":
                    tokens.append(Token(None, TT_MODULO))
                elif op == ">":
                    tokens.append(Token(None, TT_GREATER))
                elif op == "<":
                    tokens.append(Token(None, TT_LESS))
                elif op == "==":
                    tokens.append(Token(None, TT_IS_EQUAL))
                elif op == ">=":
                    tokens.append(Token(None, TT_GREATER_EQUAL))
                elif op == "<=":
                    tokens.append(Token(None, TT_LESS_EQUAL))
                elif op == "!=":
                    tokens.append(Token(None, TT_NOT_EQUAL))
                elif op == ":":
                    if i < len(text):
                        tokens.append(Token(None, TT_RANGE_TO))
                elif op == "::":
                    tokens.append(Token(None, TT_RANGE_THROUGH))
                elif op == "=":
                    tokens.append(Token(TT_EQUALS, TT_EQUALS))
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)

            # Bracket checks
            elif char == "(":
                tokens.append(Token(TT_BRACKET, TT_LPAREN))
            elif char == ")":
                tokens.append(Token(TT_BRACKET, TT_RPAREN))

            # Comment checks
            elif char == "#":
                i = len(text)
                continue

            # List checks
            elif char == "[":
                if latest is not None:
                    if latest.type == TT_VAR or latest.type == TT_INDEX:
                        index = calculate(parse(*read(text_extract(text[i:], opening="[", closing="]"))))
                        tokens.append(Token(TT_INDEX, index))
                        i += get_closing_text(text[i:], opening="[", closing="]")
                    else:
                        tokens.append(get_list(text, i))
                        i += get_closing_text(text, opening="[", closing="[")
                else:
                    tokens.append(get_list(text, i))
                    i += get_closing_text(text, opening="[", closing="]")

            # Check for start of number: syntax like ".2" is
            # not supported as of 9/6/2021: only "0.2" will
            # be accepted
            if char.isnumeric():
                # Start initial state of number reader
                number = ""
                dot_count = 0

                # Number can have digits or a decimal point
                while char.isnumeric() or char == ".":
                    # Check if number is decimal point
                    if char == ".":
                        # It is a decimal point
                        if dot_count > 0:
                            # Make sure there is only one
                            # point
                            i += 1
                            if i < len(list(text)):
                                char = text[i]
                            continue
                        else:
                            dot_count += 1
                            i += 1
                            if i < len(list(text)):
                                number += char
                                char = text[i]
                            else:
                                break
                    else:
                        # The letter is a digit
                        number += char
                        i += 1
                        if i < len(list(text)):
                            char = text[i]
                        else:
                            break
                if dot_count > 0:
                    # If there is more than 0 dots, it is a float...
                    tokens.append(Token(TT_FLOAT, float(number) * multiplier))
                else:
                    # Otherwise, it is an int.
                    tokens.append(Token(TT_INT, int(number) * multiplier))
                multiplier = 1

            # Look for variables/keywords
            # Only allowed characters are letters and underscores
            elif char.isalpha() or char == "_":
                # Set initial state for variable reader
                name = ""

                # Loop until un-matching character is found
                while char.isalpha() or char == "_":
                    # Add letters and go to next one
                    name += char
                    i += 1

                    # Make sure to not go over the end of text
                    if i < len(text):
                        char = text[i]
                    else:
                        break

                # Check if word is keyword or variable
                if name in KEYWORDS.keys():
                    kw_type = KEYWORDS[name]
                    if kw_type == TT_BOOL:
                        if name == "True":
                            name = True
                        else:
                            name = False
                    tokens.append(Token(kw_type, name))
                else:
                    tokens.append(Token(TT_VAR, name))

            # Look for strings
            elif char == "\"":
                # Set initial state
                string = r""
                if i < len(text) - 1:
                    i += 1
                    char = text[i]

                while char != "\"" and i < len(text):
                    string += char
                    i += 1
                    if i < len(text):
                        char = text[i]

                tokens.append(Token(TT_STR, string))
                i += 1
            else:
                i += 1
            if len(tokens) > 0:
                # Get latest
                latest = tokens[-1]


# Analyse tokens
def analyse_tokens(tokenized):
    """A function to make sure tokenized syntax is correct"""
    for i in range(0, len(tokenized)):
        token = tokenized[i]
        if i < len(tokenized) - 1:
            # Constructions like "8 100" are not allowed
            if token.type == TT_INT and tokenized[i + 1].type == TT_INT:
                PyscriptSyntaxError("Invalid Syntax", True)


def assign_pseudo_types(tokenized):
    """A function to assign pseudo-types to tokens after reading"""

    # Set initial state
    i = 0

    # Assignment loop
    while i < len(tokenized):
        token = tokenized[i]
        if token.type == TT_VAR:
            pseudo_type, extra_args = check_variable(tokenized, i)
            token.pseudo_type = pseudo_type
            token.extra_params = extra_args
        i += 1


def check_variable(tokenized, i):
    # If it is a variable, it can be either
    # referenced or assigned.
    if i == len(tokenized) - 1:
        # In the construction "foo = bar",
        # "bar" is referenced as it is at
        # the end.
        return PT_REFERENCE, []
    elif tokenized[i+1].type == TT_EQUALS:
        # In the construction "foo = bar",
        # "foo" is assigned as it has an
        # equals sign next to it.
        return PT_ASSIGNMENT, []
    elif tokenized[i+1].type == TT_INDEX:
        pseudo_type, extra_parameters = check_variable(tokenized, i+1)
        return indexed[pseudo_type], [tokenized[i+1].val, *extra_parameters]
    else:
        # In the construction "foobar = foo + bar",
        # "foo" is referenced as it is not succeeded
        # by an equals sign.
        return PT_REFERENCE, []


def remove_index_tokens(tokenized):
    output = tokenized[:]
    i = 0
    deletion_number = 0
    while i < len(tokenized):
        token = tokenized[i]
        if token.type == TT_INDEX:
            del output[i-deletion_number]
            deletion_number += 1
        i += 1
    return output


def text_extract(expr, opening="(", closing=")"):
    # Start initial state: i = 1 because
    # it is assumed that the first token
    # is an opening bracket.
    bracket_no = 1
    out = []
    i = 1

    # Loop
    while i < len(expr) and bracket_no > 0:
        char = expr[i]
        if char == opening:
            bracket_no += 1 if i > 0 else 0
        if char == closing:
            bracket_no -= 1

        out.append(char)
        i += 1

    del out[-1]

    return "".join(out)


def bracket_extract(expr, opening=TT_LPAREN, closing=TT_RPAREN):
    """A function to get the part between brackets"""

    # Start initial state: i = 1 because
    # it is assumed that the first token
    # is an opening bracket.
    bracket_no = 1
    out = []
    i = 1

    # Loop
    while i < len(expr) and bracket_no > 0:
        char = expr[i]
        if char.val == opening:
            bracket_no += 1 if i > 0 else 0
        if char.val == closing:
            bracket_no -= 1

        out.append(char)
        i += 1

    del out[-1]

    return out


def bracketize(tokenized, unary=False):
    output = tokenized[:]
    op_no = 0
    op_stack = []
    i = len(tokenized) - 1 if not unary else 0
    inserted = 0
    loop_condition = i >= 0 if not unary else i < len(tokenized)
    while loop_condition:
        token = tokenized[i]

        if token.type is None:
            op_no += 1
            if op_no > 1:
                if not unary:
                    if token.val not in un_ops:
                        if tokenized[i + 1].type == TT_BRACKET:
                            output.insert(get_closing(tokenized[i + 1:]) + i + 2 + (op_no - 2), Token(TT_BRACKET,
                                                                                                      TT_RPAREN))
                        else:
                            output.insert(i + 2 + (op_no - 2), Token(TT_BRACKET, TT_RPAREN))
                        output.insert(0, Token(TT_BRACKET, TT_LPAREN))
                else:
                    if token.val in un_ops:
                        output.insert(i + (op_no - 2), Token(TT_BRACKET, TT_LPAREN))
                        output.append(Token(TT_BRACKET, TT_RPAREN))
                inserted += 1
        elif token.val == TT_RPAREN:
            if not unary:
                op_stack.append(op_no)
                op_no = 0
        elif token.val == TT_LPAREN:
            if not unary:
                op_no = op_stack.pop(len(op_stack) - 1)
        elif token.type == "DUMMY":
            if not unary:
                token.val = bracketize(token.val)[0]

        i += 1 if unary else -1
        loop_condition = i >= 0 if not unary else i < len(tokenized)
    return output, inserted


def get_closing(expr, opening=TT_LPAREN, closing=TT_RPAREN):
    bracket_no = 1
    i = 1
    while i < len(expr) and bracket_no > 0:
        char = expr[i]
        if char.val == opening:
            bracket_no += 1 if i > 0 else 0
        if char.val == closing:
            bracket_no -= 1
        i += 1

    return i - 1


def get_opening(expr, opening=TT_LPAREN, closing=TT_RPAREN):
    bracket_no = 1
    i = len(expr) - 2
    while i > 0 and bracket_no > 0:
        char = expr[i]
        if char.val == closing:
            bracket_no += 1 if i > 0 else 0
        if char.val == opening:
            bracket_no -= 1
        i -= 1

    return i + 1


def get_closing_text(expr, opening="(", closing=")"):
    bracket_no = 1
    i = 1
    while i < len(expr) and bracket_no > 0:
        char = expr[i]
        if char == opening:
            bracket_no += 1 if i > 0 else 0
        if char == closing:
            bracket_no -= 1
        i += 1

    return i - 1


def pre_parse(tokenized):
    i = 0
    while i < len(tokenized):
        token = tokenized[i]
        if token.pseudo_type == PT_REFERENCE:
            var_exists = False
            for var in global_vars:
                if token.val == var.name:
                    tokenized[i] = Token(TT_INT, var.value)
                    var_exists = True
            if not var_exists:
                PyscriptNameError(f"variable '{token.val}' was referenced before assignment", True)
        elif token.pseudo_type == PT_ASSIGNMENT:
            found_var = None
            for var in global_vars:
                if token.val == var.name:
                    found_var = var
            if found_var is not None and found_var.readonly:
                PyscriptAssignmentError(f"AssignmentError: Editing readonly variable '{found_var.name}'", True)
        elif token.pseudo_type == PT_INDEX_REFERENCE:
            var_exists = False
            for var in global_vars:
                if token.val == var.name:
                    element = None
                    if type(token.extra_params[0]) == int:
                        if token.extra_params[0] > len(var.value):
                            PyscriptIndexError(f"Index {token.extra_params[0]} is out of range", True)
                        element = var.value[token.extra_params[0]]
                    elif type(token.extra_params[0]) == list:
                        temp = var.value
                        element = []
                        for j in token.extra_params[0]:
                            if j > len(temp)-1:
                                PyscriptIndexError(f"Index {j} is out of range", True)
                            else:
                                element.append(temp[j])
                    if len(token.extra_params) > 1:
                        for index in token.extra_params[1:]:
                            if type(element) != list:
                                PyscriptSyntaxError("Invalid Syntax", True)
                            if type(index) == int:
                                element = element[index]
                            elif type(index) == list:
                                temp = element.value
                                element.value = []
                                for i in index:
                                    if i > len(temp):
                                        PyscriptIndexError(f"Index {token.extra_params[0]} is out of range", True)
                                    else:
                                        element.value.append(temp[i])
                    tokenized[i] = Token(TT_INT, element)

                    var_exists = True
            if not var_exists:
                PyscriptNameError(f"variable '{token.val}' was referenced before assignment", True)

        i += 1


def parse(tokenized, raw=None, count=0, level_condition=None):
    pre_parse(tokenized)
    if raw is None:
        raw = tokenized[:]
    result = [tokenized[0]]

    if len(tokenized) == 1 and tokenized[0].type in types:
        return ValueNode(tokenized[0].val)

    i = 0
    readonly_flag = False
    while i < len(tokenized):
        token = tokenized[i]
        previous = None
        next = None

        if i > 0:
            previous = tokenized[i - 1]
        if i < len(tokenized) - 1:
            next = tokenized[i + 1]

        if token.type is None:
            if token.val not in un_ops:
                if next is None or previous is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
            else:
                if next is None:
                    PyscriptSyntaxError("Invalid Syntax", True)

            previous_node = None
            next_node = None
            if next is not None:
                next_node = next.val
                if next.val == TT_LPAREN:
                    next_node = parse(bracket_extract(tokenized[i + 1:]))
                    i = get_closing(tokenized[i + 1:]) + i + 1
            if previous is not None:
                previous_node = previous.val
                if previous.val == TT_RPAREN:
                    previous_node = result

            if token.val == TT_PLUS:
                result = BinOpNode(previous_node, next_node, "+", lambda a, b: a + b)
            elif token.val == TT_MINUS:
                result = BinOpNode(previous_node, next_node, "-", lambda a, b: a - b)
            elif token.val == TT_MUL:
                result = BinOpNode(previous_node, next_node, "*", lambda a, b: a * b)
            elif token.val == TT_DIV:
                result = BinOpNode(previous_node, next_node, "/", lambda a, b: a / b)
            elif token.val == TT_POWER:
                result = BinOpNode(previous_node, next_node, "^", lambda a, b: a ** b)
            elif token.val == TT_MODULO:
                result = BinOpNode(previous_node, next_node, "%", lambda a, b: a % b)

            elif token.val == TT_RANGE_TO:
                result = BinOpNode(previous_node, next_node, ":", lambda a, b: range_from_to(a, b))
            elif token.val == TT_RANGE_THROUGH:
                result = BinOpNode(previous_node, next_node, "::", lambda a, b: range_from_to(a, b+1))

            elif token.val == TT_GREATER:
                result = BinOpNode(previous_node, next_node, ">", lambda a, b: a > b)
            elif token.val == TT_LESS:
                result = BinOpNode(previous_node, next_node, "<", lambda a, b: a < b)
            elif token.val == TT_IS_EQUAL:
                result = BinOpNode(previous_node, next_node, "==", lambda a, b: a == b)
            elif token.val == TT_LESS_EQUAL:
                result = BinOpNode(previous_node, next_node, "<=", lambda a, b: a <= b)
            elif token.val == TT_GREATER_EQUAL:
                result = BinOpNode(previous_node, next_node, ">=", lambda a, b: a >= b)
            elif token.val == TT_NOT_EQUAL:
                result = BinOpNode(previous_node, next_node, "!=", lambda a, b: a != b)

            elif token.val == KW_AND:
                result = BinOpNode(previous_node, next_node, "and", lambda a, b: a and b)
            elif token.val == KW_OR:
                result = BinOpNode(previous_node, next_node, "or", lambda a, b: a or b)
            elif token.val == KW_XOR:
                result = BinOpNode(previous_node, next_node, "xor", lambda a, b: (a or b) and not (a and b))
            elif token.val == KW_NOT:
                result = UnOpNode(next_node, "not", lambda a: not a)
        elif token.type == TT_EQUALS:
            if previous is not None:
                if previous.type == TT_VAR:
                    if previous.pseudo_type == PT_ASSIGNMENT:
                        name = previous.val
                        bracketized = prep_unary(raw[i + 1 - count:])
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        value = calculate(parse(bracketized))
                        local_flag = readonly_flag
                        result = BinOpNode(name, value, "=", lambda a, b: set_var(a, b, local_flag))
                        return result
                    elif previous.pseudo_type == PT_INDEX_ASSIGNMENT:
                        name = previous.val
                        bracketized = prep_unary(raw[i + 1 - count:])
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        value = calculate(parse(bracketized))
                        result = BinOpNode(name, value, "=", lambda a, b: index_set_var(a, b, previous.extra_params))
                        return result
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            else:
                PyscriptSyntaxError("Invalid Syntax", True)
        elif token.type == TT_KEYWORD:
            if token.val == KW_READONLY:
                if i < len(tokenized) - 1:
                    if tokenized[i + 1].type == TT_VAR:
                        readonly_flag = True
                    else:
                        PyscriptSyntaxError("Invalid Syntax", True)
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_CONTINUE:
                return None, KW_CONTINUE
        elif token.type == TT_BRANCH:
            if token.val == KW_IF:
                bracketized = prep_unary(raw[i + 1 - count:])
                bracketized, unused = bracketize(bracketized)
                bracketized = unwrap_unary(bracketized)
                condition = calculate(parse(bracketized))
                if type(condition) != bool:
                    PyscriptSyntaxError("Invalid Syntax", True)
                else:
                    return condition, TT_BRANCH
            if token.val == KW_ELSE:
                if level_condition is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
                return not level_condition
        elif token.type == TT_WHILE:
            bracketized = prep_unary(raw[i + 1 - count:])
            bracketized, unused = bracketize(bracketized)
            bracketized = unwrap_unary(bracketized)
            condition = calculate(parse(bracketized))
            if type(condition) != bool:
                PyscriptSyntaxError("Invalid Syntax", True)
            else:
                return condition, TT_WHILE
        i += 1
    return result


def calculate(node):
    return node.get_value()
