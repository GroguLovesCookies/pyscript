# Imports
from os import access
from errors import *
from vars import *
from labels import *
from nodes import *
from range import range_from_to
from typing import List, Dict, Tuple, Union
from inliner import *
from utility_classes.var_data import VarData
from token_def import TokDef
from shared_vars import *


# Define tokens
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POWER = "POWER"
TT_MODULO = "MOD"
TT_FLOOR_DIV = "FLOOR_DIV"
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
TT_COMMA = "COMMA"
TT_COLON_END = "COL_END"
TT_SEMICOLON = "SEMICOLON"
TT_INSERTION = "INSERTION"
TT_PERIOD = "PERIOD"

# Define pseudo-types
PT_ASSIGNMENT = "ASSIGNING"
PT_REFERENCE = "REFERENCING"
PT_DEL = "DELETING"
PT_INDEX_ASSIGNMENT = "INDEX_ASSIGN"
PT_INDEX_REFERENCE = "INDEX_REFERENCE"
PT_USING_ASSIGN = "USING_ASSIGN"
PT_USING_REFERENCE = "USING_REFERENCE"
PT_OUT = "PUSHING_OUT"
PT_GLOBAL = "GLOBAL"
PT_ARGUMENT = "ARG"
PT_CALLED = "CALLED"
PT_ACCESSED = "ACCESSED"

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
KW_BREAK = "break"
KW_LABEL = "label"
KW_JUMP = "jump"
KW_CALL = "call"
KW_DEF_LABEL = "def_label"
KW_IN = "in"
KW_NOT_IN = "not in"
KW_USING = "using"
KW_DEL = "del"
KW_LOCAL = "local"
KW_OUT = "out"
KW_OUTER = "outer"
KW_SCOPE_RESOLUTION = "scope_res"
KW_FOR = "for"
KW_FUNC = "func"
KW_EXTERN = "extern"
KW_RETURN = "return"
KW_IMPORT = "import"
KW_AS = "as"
KW_INLINE = "inline"
KW_INDESTRUCTIBLE = "indestructible"
KW_LET = "let"
KW_BE = "be"
KW_REM_KW = "rem_keyword"
KW_FROM = "from"
KW_SWITCH = "switch"
KW_CASE = "case"
KW_HIDDEN = "hidden"
KW_ASSERT = "assert"
KEYWORDS: Dict = {KW_READONLY: TT_KEYWORD, KW_TRUE: TT_BOOL, KW_FALSE: TT_BOOL, KW_AND: None, KW_OR: None, KW_XOR: None,
                  KW_NOT: None, KW_IF: TT_BRANCH, KW_ELSE: TT_BRANCH, KW_WHILE: TT_WHILE, KW_CONTINUE: TT_KEYWORD,
                  KW_BREAK: TT_KEYWORD, KW_LABEL: TT_KEYWORD, KW_DEF_LABEL: TT_KEYWORD, KW_JUMP: TT_KEYWORD,
                  KW_CALL: TT_KEYWORD, KW_IN: None, KW_NOT_IN: None, KW_USING: TT_KEYWORD, KW_DEL: TT_KEYWORD,
                  KW_LOCAL: TT_KEYWORD, KW_OUT: TT_KEYWORD, KW_OUTER: None, KW_FOR: TT_KEYWORD, KW_FUNC: TT_KEYWORD,
                  KW_EXTERN: TT_KEYWORD, KW_RETURN: TT_KEYWORD, KW_IMPORT: TT_KEYWORD, KW_AS: TT_KEYWORD,
                  KW_INLINE: TT_KEYWORD, KW_INDESTRUCTIBLE: TT_KEYWORD, KW_LET: TT_KEYWORD, KW_BE: TT_KEYWORD,
                  KW_REM_KW: TT_KEYWORD, KW_FROM: TT_KEYWORD, KW_SWITCH: TT_KEYWORD, KW_CASE: TT_KEYWORD,
                  KW_HIDDEN: TT_KEYWORD, KW_ASSERT: TT_KEYWORD}

compound_kws: Dict[str, List[str]] = {KW_NOT_IN: [KW_NOT, KW_IN]}

# Define types
types: List[str] = [TT_INT, TT_FLOAT, TT_STR, TT_LIST, TT_BOOL]
hashable_types: List[str] = [TT_INT, TT_FLOAT, TT_STR, TT_BOOL]


# Define operator list
op_chars: List[chr] = ["+", "-", "*", "/", "^", "%", "=", ">", "<", "!", ":", ",", ";", "."]

# Define indexed versions of un-indexed pseudo-types
indexed: Dict[str, str] = {PT_ASSIGNMENT: PT_INDEX_ASSIGNMENT, PT_REFERENCE: PT_INDEX_REFERENCE,
                           PT_INDEX_ASSIGNMENT: PT_INDEX_ASSIGNMENT, PT_INDEX_REFERENCE: PT_INDEX_REFERENCE}


# Class Token
class Token:
    """A class to define properties of tokens used by the lexer"""

    def __init__(self, tok_type, val):
        self.val = val
        self.type = tok_type
        self.pseudo_type = None
        self.extra_params: List = []

    def __repr__(self) -> str:
        if self.type is None:
            return self.val
        return f"{self.type}:{self.val}"


def register_func(name):
    un_ops.add(name)
    funcs.add(name)


func_to_register = register_func


def prep_unary(tokenized: List[Token]) -> List[Token]:
    """A function that combines unary sequences into single units"""

    # Initialize
    start_index_stack: List[int] = []
    i: int = 0
    start_index: int = -1
    insert_number: int = 0
    # Loop
    while i < len(tokenized):
        token: Token = tokenized[i]
        # Lists are not parts of unary sequences
        if type(token.val) == list:
            i += 1
            continue
        if token.val in un_ops:
            # If it's a unary operator
            if token.val in funcs:
                # If it's a function
                if token.pseudo_type != PT_CALLED:
                    # If it's not being called, then it does not act as a unary operator
                    # but a variable, therefore skip
                    i += 1
                    continue
            if start_index < 0:
                # Remember start index of unary sequence
                start_index = i
        else:
            if token.val == TT_LPAREN:
                # If it's a opening bracket, then remember start_index for later to
                # allow for nested unary sequences
                start_index_stack.append(start_index)
                start_index = -1
            elif token.val == TT_RPAREN:
                # If it's a closing bracket, then get start_index for previous unary sequence
                start_index = start_index_stack.pop()
            elif start_index >= 0:
                # Calculate end index based on number of inserts
                change: int = insert_number
                if insert_number > 0:
                    change -= 1
                # Get unary sequence
                thing: List[Token] = tokenized[start_index: i + 1 - change]
                # Delete all but one element of the sequence and change i
                del tokenized[start_index: i - change]
                i -= len(thing) - 1
                # Assign the unit to the remaining element of the sequence
                tokenized[start_index] = Token(TT_UNIT, thing)
                # Change insert number and reset start_index as unary sequence is completed
                insert_number += 1
                start_index = -1
        i += 1
    if start_index >= 0:
        # If there is a unary sequence leftover at the end, then do this
        change: int = insert_number
        if insert_number > 0:
            change -= 1
        thing: List[Token] = tokenized[start_index: i + 1 - change]
        del tokenized[start_index: i - change]
        tokenized.append(Token(TT_UNIT, thing))
    return tokenized


def unwrap_unary(tokenized: List[Token]) -> List[Token]:
    """A function to unwrap and re-bracketize unary sequences"""
    # Initalize
    i: int = 0
    # Loop
    while i < len(tokenized):
        token: Token = tokenized[i]
        # If it is a combined unary sequence...
        if token.type == TT_UNIT:
            # Delete the unit
            del tokenized[i]
            # Insert brackets and re-insert combined unary sequence
            tokenized.insert(i, Token(TT_BRACKET, TT_RPAREN))
            for item in reversed(bracketize(token.val, True)[0]):
                tokenized.insert(i, item)
            tokenized.insert(i, Token(TT_BRACKET, TT_LPAREN))
        i += 1
    return tokenized


def split_list(text: str, character: str = " ", strip: bool = False) -> List[str]:
    """A function to split lists from text"""
    splitted: List[str] = []
    quote_ignore: bool = False
    bracket_ignore: bool = False
    current: str = ""

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
            # Not quote_ignore in order to ignore the split character if it
            # occurs in  a string
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


def get_list(text: str, i: int) -> Token:
    """A function to get a list from text"""
    # Read full list
    listed: List[List[Token]] = read(text_extract(text[i:], opening="[", closing="]"), ignore_exception=True, group_by=",")
    i = get_closing_text(text[i:], "[", "]") + i
    j: int = 0
    while j < len(listed):
        # Calculate each set of tokens
        listed[j] = calculate(parse(listed[j]))
        j += 1
    return Token(TT_LIST, listed)


# Reading function
def read(text: str, ignore_exception: bool = False, group_by: str = "") -> List[Token]:
    """A function to tokenize input text"""

    if group_by != "":
        results: List[List[Token]] = [read(item)[0] for item in split_list(text, ",", True)]
        return results
    else:
        # Set initial state
        is_remove: bool = False
        tokens: List[Token] = []
        i: int = 0
        multiplier: int = 1
        latest: Token = None

        # Read loop
        while True:
            # If at the end of list, make sure of correct
            # syntax, add implicit bracketing, and return
            if i >= len(list(text)):
                if not ignore_exception:
                    analyse_tokens(tokens)
                tokens = compound_operators(tokens)
                raw: List[Token] = tokens[:]
                assign_pseudo_types(tokens)
                assign_pseudo_types(raw)
                tokens = prep_unary(tokens)
                tokens, count = bracketize(tokens)
                tokens = unwrap_unary(tokens)
                tokens = remove_index_tokens(tokens)
                raw = remove_index_tokens(raw)
                return tokens, raw, count

            # Analyse character
            char: chr = text[i]
            # Operator checks
            if char in op_chars:
                op: str = ""
                # Compounds chars to find longest match
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
                    elif latest.type is None or latest.val in [TT_LPAREN, KW_RETURN] or latest.type == TT_EQUALS:
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
                    else:
                        tokens.append(Token(TT_COLON_END, TT_RANGE_TO))
                elif op == "::":
                    tokens.append(Token(None, TT_RANGE_THROUGH))
                elif op == "=":
                    tokens.append(Token(TT_EQUALS, TT_EQUALS))
                elif op == ",":
                    tokens.append(Token(TT_COMMA, TT_COMMA))
                elif op == ";":
                    tokens.append(Token(TT_SEMICOLON, TT_SEMICOLON))
                elif op == "//":
                    tokens.append(Token(None, TT_FLOOR_DIV))
                elif op == "->":
                    tokens.append(Token(TT_INSERTION, TT_INSERTION))
                elif op == ".":
                    tokens.append(Token(TT_PERIOD, TT_PERIOD))
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
                continue

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
                        index: int = calculate(parse(*read(text_extract(text[i:], opening="[", closing="]"))))
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
                number: str = ""
                dot_count: int = 0

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
                name: str = ""

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
                    if name == KW_REM_KW:
                        # is_remove flag disables expansion of TokDefs
                        is_remove = True
                    kw_type: str = KEYWORDS[name]
                    if kw_type == TT_BOOL:
                        # Builtin bool() doesn't seem to work
                        if name == "True":
                            name = True
                        else:
                            name = False
                    if name == KW_OUTER:
                        # Outer is a conman, if the previous token is an outer, then it should behave
                        # differently from when latest token is not an outer
                        if latest.val == KW_OUTER or latest.val == KW_SCOPE_RESOLUTION:
                            name = KW_SCOPE_RESOLUTION
                    tokens.append(Token(kw_type, name))
                else:
                    # It's either a variable or a TokDef
                    # so find a TokDef
                    token_definition = TokDef.FindTokDef(name)
                    if token_definition is None or is_remove:
                        # If one is found or it is a rem_keyword then
                        # It is a var...
                        tokens.append(Token(TT_VAR, name))
                    else:
                        # Otherwise it's a TokDef so expand it
                        for tok in token_definition.definition:
                            tokens.append(tok)

            # Look for strings
            elif char == "\"":
                # Set initial state
                string: str = r""
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
def analyse_tokens(tokenized: List[Token]):
    """A function to make sure tokenized syntax is correct"""
    for i in range(0, len(tokenized)):
        token = tokenized[i]
        if i < len(tokenized) - 1:
            # Constructions like "8 100" are not allowed
            if token.type == tokenized[i + 1].type and token.type in types:
                PyscriptSyntaxError("Invalid Syntax", True)


def compound_operators(tokenized: List[Token]) -> List[Token]:
    """A function to combine tokens like 'not' and 'in' to 'not in'"""
    for item in compound_kws.items():
        pattern: List[str] = item[1]
        keyword: str = item[0]
        i: int = 0
        match_index: int = 0
        match_start: int = -1
        while i < len(tokenized):
            # If it matches the pattern so far...
            if tokenized[i].val == pattern[match_index]:
                if match_index == 0:
                    # and it's the beginning of a match then set match_start...
                    match_start = i
                # ...if it's not the beginning increment match_index
                match_index += 1
                if match_index == len(pattern):
                    # If it is the full length of the pattern, then combine it
                    del tokenized[match_start: i]
                    tokenized[match_start] = Token(KEYWORDS[keyword], keyword)
            else:
                # Otherwise any match so far is bogus so reset
                match_index = 0
                match_start = -1
            i += 1
    return tokenized


def assign_pseudo_types(tokenized: List[Token]):
    """A function to assign pseudo-types to tokens after reading"""

    # Set initial state
    i: int = 0
    var_data: VarData = VarData.default.duplicate()

    # Assignment loop
    while i < len(tokenized):
        token: Token = tokenized[i]
        # Check what statement type it is
        if token.val == KW_USING:
            var_data.set("is_using", True)
        if token.val == KW_DEL:
            var_data.set("is_del", True)
        if token.val == KW_OUT:
            var_data.set("is_out", True)
        if token.val == KW_FOR:
            var_data.set("is_for", True)
        if token.val == TT_SEMICOLON:
            var_data.set("is_for", False)
        if token.val == KW_FUNC:
            var_data.set("is_func", True)
        if token.type == TT_VAR:
            # If it is a var then find its pseudo-type
            pseudo_type, extra_args = check_variable(tokenized, i, var_data)
            if pseudo_type == PT_CALLED:
                token.type = None
            token.pseudo_type = pseudo_type
            token.extra_params = extra_args
        i += 1


def check_variable(tokenized: List[Token], i: int, var_data: VarData = VarData.default) -> Tuple[str, List[int]]:
    # If it is a variable, it can be either
    # referenced or assigned.
    # That was long ago, now it can be deleted, used, indexed, blah blah blah
    is_using = var_data.is_using
    is_del = var_data.is_del
    is_out = var_data.is_out
    is_for = var_data.is_for
    is_func = var_data.is_func
    if i == len(tokenized) - 1:
        # In the construction "foo = bar",
        # "bar" is referenced as it is at
        # the end.
        if is_using:
            return PT_USING_REFERENCE, []
        if is_del:
            return PT_DEL, []
        if is_out:
            return PT_OUT, []
        if is_func:
            return PT_ARGUMENT, []
        return PT_REFERENCE, []
    elif tokenized[i + 1].type == TT_EQUALS:
        # In the construction "foo = bar",
        # "foo" is assigned as it has an
        # equals sign next to it.
        if is_using:
            return PT_USING_ASSIGN, []
        if is_del:
            PyscriptSyntaxError("Deleting assigned variable", True)
        if is_out:
            PyscriptSyntaxError("Pushing assigned variable", True)
        if is_for:
            set_var(tokenized[i].val, 0)
        if is_func:
            PyscriptSyntaxError("Invalid Syntax", True)  # Default argument values come later
        return PT_ASSIGNMENT, []
    elif tokenized[i - 1].val == KW_OUTER or tokenized[i - 1].val == KW_SCOPE_RESOLUTION:
        # outer x or outer outer x mean that it is accessed from a previous scope
        return PT_GLOBAL, []
    elif tokenized[i - 1].type == TT_EQUALS:
        if tokenized[i + 1].type != TT_INDEX:
            if tokenized[i + 1].val == TT_LPAREN:
                return PT_CALLED, [bracket_extract(tokenized[i + 1:])]
            return PT_REFERENCE, []
        pseudo_type, extra_parameters = check_variable(tokenized, i + 1)
        return PT_INDEX_REFERENCE, [tokenized[i + 1].val, *extra_parameters]
    elif tokenized[i + 1].type == TT_INDEX:
        if is_using:
            PyscriptSyntaxError("Cannot have index in 'using' context", True)
        if is_del:
            PyscriptSyntaxError("Cannot delete index with 'del'", True)
        if is_func:
            PyscriptSyntaxError("Invalid Syntax", True)
        pseudo_type, extra_parameters = check_variable(tokenized, i + 1)
        return indexed[pseudo_type], [tokenized[i + 1].val, *extra_parameters]
    else:
        # In the construction "foobar = foo + bar",
        # "foo" is referenced as it is not succeeded
        # by an equals sign.
        if is_using:
            return PT_USING_REFERENCE, []
        if is_del:
            return PT_DEL, []
        if is_out:
            return PT_OUT, []
        if is_func:
            return PT_ARGUMENT, []
        if tokenized[i + 1].val == TT_LPAREN:
            return PT_CALLED, [bracket_extract(tokenized[i + 1:])]
        return PT_REFERENCE, []


def remove_index_tokens(tokenized: List[Token]) -> List[Token]:
    output: List[Token] = tokenized[:]
    i: int = 0
    deletion_number: int = 0
    while i < len(tokenized):
        token: Token = tokenized[i]
        if token.type == TT_INDEX:
            del output[i - deletion_number]
            deletion_number += 1
        i += 1
    return output


def text_extract(expr: str, opening: chr = "(", closing: chr = ")") -> str:
    # Start initial state: i = 1 because
    # it is assumed that the first token
    # is an opening bracket.
    bracket_no: int = 1
    out: List[chr] = []
    i: int = 1

    # Loop
    while i < len(expr) and bracket_no > 0:
        char: chr = expr[i]
        if char == opening:
            bracket_no += 1 if i > 0 else 0
        if char == closing:
            bracket_no -= 1

        out.append(char)
        i += 1

    del out[-1]

    return "".join(out)


def bracket_extract(expr: List[Token], opening: str = TT_LPAREN, closing: str = TT_RPAREN) -> List[Token]:
    """A function to get the part between brackets"""

    # Start initial state: i = 1 because
    # it is assumed that the first token
    # is an opening bracket.
    bracket_no: int = 1
    out: List[Token] = []
    i: int = 1

    # Loop
    while i < len(expr) and bracket_no > 0:
        token: int = expr[i]
        if token.val == opening:
            bracket_no += 1 if i > 0 else 0
        if token.val == closing:
            bracket_no -= 1

        out.append(token)
        i += 1

    del out[-1]

    return out


def bracketize(tokenized: List[Token], unary: bool = False) -> Tuple[List[Token], int]:
    output: List[Token] = tokenized[:]
    op_no: int = 0
    op_stack: List[int] = []
    i: int = len(tokenized) - 1 if not unary else 0
    inserted: int = 0
    loop_condition: int = i >= 0 if not unary else i < len(tokenized)
    while loop_condition:
        token: Token = tokenized[i]

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


def get_closing(expr: List[Token], opening: str = TT_LPAREN, closing: str = TT_RPAREN) -> int:
    bracket_no: int = 1
    i: int = 1
    while i < len(expr) and bracket_no > 0:
        token: Token = expr[i]
        if token.val == opening:
            bracket_no += 1 if i > 0 else 0
        if token.val == closing:
            bracket_no -= 1
        i += 1

    return i - 1


def get_opening(expr: List[Token], opening: str = TT_LPAREN, closing: str = TT_RPAREN) -> int:
    bracket_no: int = 1
    i: int = len(expr) - 2
    while i > 0 and bracket_no > 0:
        token: Token = expr[i]
        if token.val == closing:
            bracket_no += 1 if i > 0 else 0
        if token.val == opening:
            bracket_no -= 1
        i -= 1

    return i + 1


def get_closing_text(expr: str, opening: chr = "(", closing: chr = ")") -> int:
    bracket_no: int = 1
    i: int = 1
    while i < len(expr) and bracket_no > 0:
        char: chr = expr[i]
        if char == opening:
            bracket_no += 1 if i > 0 else 0
        if char == closing:
            bracket_no -= 1
        i += 1

    return i - 1


def split_list_by_token(tok_type: str, tok_val, tokenized: List[Token], index: int = 0) -> List[List[Token]]:
    splitted: List[List[Token]] = []
    current_split: List[Token] = []
    cur_index = 0
    i = 0
    if index == -1:
        for ind, tok in enumerate(tokenized):
            if tok.val == tok_val and tok.type == tok_type:
                index += 1
    while i < len(tokenized):
        token = tokenized[i]
        if token.type == tok_type and token.val == tok_val:
            if cur_index == index or index == 0:
                splitted.append(current_split)
                current_split = []
            else:
                current_split.append(token)
                cur_index += 1
            i += 1
            continue
        if token.val == TT_LPAREN:
            current_split.append(token)
            current_split.extend(bracket_extract(tokenized[i:]))
            i += get_closing(tokenized[i:])
            continue
        current_split.append(token)
        i += 1
    splitted.append(current_split)
    return splitted


def make_path(pyscript_path: List[Token]) -> str:
    sections: List[List[Token]] = split_list_by_token(TT_PERIOD, TT_PERIOD, pyscript_path)
    path: str = ""
    for i, section in enumerate(sections):
        if len(section) != 1:
            PyscriptSyntaxError("Invalid Syntax", True)
        path += section[0].val
        path += "/" if i < len(sections)-1 else ".pyscript"
    return path


def pre_parse(tokenized: List[Token], extra_vars=None):
    if extra_vars is None:
        extra_vars = {}
    i: int = 0
    while i < len(tokenized):
        token: Token = tokenized[i]
        if token.val in [KW_LABEL, KW_JUMP, KW_CALL, KW_DEF_LABEL, KW_IMPORT, KW_LET, KW_REM_KW]:
            return
        if token.type == TT_PERIOD:
            tokenized[i-1].pseudo_type = PT_ACCESSED
            i += 2
            continue
        if i < len(tokenized) - 1:
            if tokenized[i+1].type == TT_PERIOD:
                i += 1
                continue
        if token.pseudo_type == PT_REFERENCE:
            var_exists: bool = False
            if token.val in extra_vars.keys():
                tokenized[i] = Token(TT_INT, extra_vars[token.val])
                var_exists = True
            for var in global_vars:
                if token.val == var.name:
                    tokenized[i] = Token(TT_INT, var.value)
                    var_exists = True
            if not var_exists:
                PyscriptNameError(f"variable '{token.val}' was referenced before assignment", True)
        elif token.pseudo_type == PT_ASSIGNMENT:
            found_var: Variable = None
            for var in global_vars:
                if token.val == var.name:
                    found_var = var
            if found_var is not None and found_var.readonly[0]:
                PyscriptAssignmentError(f"Editing readonly variable '{found_var.name}'", True)
        elif token.pseudo_type == PT_INDEX_REFERENCE:
            var_exists: bool = False
            for var in global_vars:
                if token.val == var.name:
                    element = None
                    if type(token.extra_params[0]) == int:
                        if token.extra_params[0] > len(var.value):
                            PyscriptIndexError(f"Index {token.extra_params[0]} is out of range", True)
                        element = var.value[token.extra_params[0]]
                    elif type(token.extra_params[0]) == list:
                        temp = var.value
                        element: List = []
                        for j in token.extra_params[0]:
                            if j > len(temp) - 1:
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


def parse(tokenized: List[Token], raw: List[Token] = None, count: int = 0, extra_vars=None,
          is_nested_call: bool = False) -> Union[Node, Tuple, Label, TokDef]:
    if extra_vars is None:
        extra_vars = {}
    pre_parse(tokenized, extra_vars)
    if raw is None:
        raw = tokenized[:]
    result: Node = [tokenized[0]]

    if len(tokenized) == 1 and (tokenized[0].type in types or tokenized[0].pseudo_type == PT_GLOBAL):
        return ValueNode(tokenized[0].val)

    i: int = 0
    readonly_flag: bool = False
    indestructible_flag: bool = False
    hidden_flag: bool = False
    imported: bool = False
    imported_var: str = ""
    while i < len(tokenized):
        token: Token = tokenized[i]
        previous: Token = None
        next_token: Token = None

        if i > 0:
            previous = tokenized[i - 1]
        if i < len(tokenized) - 1:
            next_token = tokenized[i + 1]

        if token.type is None:
            if token.val not in un_ops:
                if next_token is None or previous is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
            else:
                if next_token is None:
                    PyscriptSyntaxError("Invalid Syntax", True)

            previous_node: Node = None
            next_node: Node = None
            if next_token is not None and token.val not in funcs:
                next_node = next_token.val
                if next_token.val == TT_LPAREN:
                    next_node = parse(bracket_extract(tokenized[i + 1:]), extra_vars=extra_vars)
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
            elif token.val == TT_FLOOR_DIV:
                result = BinOpNode(previous_node, next_node, "//", lambda a, b: a // b)

            elif token.val == TT_RANGE_TO:
                result = BinOpNode(previous_node, next_node, ":", lambda a, b: range_from_to(a, b))
            elif token.val == TT_RANGE_THROUGH:
                result = BinOpNode(previous_node, next_node, "::", lambda a, b: range_from_to(a, b + 1))

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

            elif token.val == KW_IN:
                if previous.type not in hashable_types or type(next_token.val) != list:
                    PyscriptSyntaxError("Invalid Syntax", True)
                result = BinOpNode(previous_node, next_node, "in", lambda a, b: a in b)
            elif token.val == KW_NOT_IN:
                if previous.type not in hashable_types or type(next_token.val) != list:
                    PyscriptSyntaxError("Invalid Syntax", True)
                result = BinOpNode(previous_node, next_node, "not in", lambda a, b: a not in b)
            if token.val == KW_OUTER:
                if type(next_node) != str:
                    PyscriptSyntaxError("Invalid Syntax", True)
                result = UnOpNode(next_node, "outer", lambda a: get_var_from_previous_scope(a))
            if token.val == KW_SCOPE_RESOLUTION:
                if type(next_node) != str:
                    PyscriptSyntaxError("Invalid Syntax", True)
                shift_scope_pointer(-1)
                result = next_node
            if token.val in funcs:
                func_to_run: Variable = get_var(token.val if not imported else "0"+token.val)
                if func_to_run == -1:
                    PyscriptNameError(f"Function '{token.val}' does not exist", True)
                args_dict: Dict[str, ] = {}
                arg_count: int = len(func_to_run.extra_args) - (1 if func_to_run.run_func == exec else 2)
                args: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, token.extra_params[0])
                for index, arg in enumerate(args):
                    if len(arg) == 0 and len(args) == 1:
                        break
                    bracketized: List[Token] = prep_unary(arg)
                    bracketized, unused = bracketize(bracketized)
                    bracketized = unwrap_unary(bracketized)
                    args_dict[func_to_run.extra_args[index + (1 if func_to_run.run_func == exec else 2)]] = calculate(
                        parse(bracketized, extra_vars=extra_vars))
                    i += len(bracketized)+1
                if len(args_dict) != arg_count:
                    PyscriptSyntaxError(
                        f"Function '{func_to_run.name}' expects {arg_count} arguments but {len(args_dict)} were "
                        f"given", True)
                inline_flag: bool = func_to_run.extra_args[1 if func_to_run.run_func != exec else 0]
                if not inline_flag or func_to_run.run_func == exec:
                    if is_nested_call:
                        args_dict.update(extra_vars)
                    result = UnOpNode(func_to_run, "run", lambda a: a.run(args_dict))
                else:
                    if is_nested_call:
                        args_dict.update(extra_vars)
                    result = parse(func_to_run.get_inline_form(args_dict, read), extra_vars=args_dict)
                if i+2 < len(tokenized):
                    if tokenized[i+2].val == TT_LPAREN:
                        function_to_call_again = calculate(result)
                        if type(function_to_call_again) != Variable:
                            PyscriptSyntaxError(f"Result of {func_to_run.name} is not callable")
                        created = set_var("00"+function_to_call_again.name, function_to_call_again)[1]
                        un_ops.add(created.name)
                        funcs.add(created.name)
                        value_to_calculate = raw[i+1-count:]
                        value_to_calculate[0].val = created.name
                        value_to_calculate[0].type = None
                        value_to_calculate[0].pseudo_type = PT_CALLED
                        value_to_calculate[0].extra_params = [bracket_extract(tokenized[i+2:])]
                        del value_to_calculate[-1]
                        bracketized: List[Token] = prep_unary(value_to_calculate)
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        result = parse(bracketized, extra_vars=args_dict, is_nested_call=True)
                        remove_var(created.name)
                        un_ops.remove(created.name)
                        funcs.remove(created.name)
                if imported:
                    remove_var(imported_var)
                    funcs.remove(token.val)
                imported = False

        elif token.type == TT_EQUALS:
            if previous is not None:
                if previous.type == TT_VAR:
                    if previous.pseudo_type in [PT_ASSIGNMENT, PT_USING_ASSIGN]:
                        name: str = previous.val
                        bracketized: List[Token] = prep_unary(raw[i + 1 - count:])
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        value = calculate(parse(bracketized, extra_vars=extra_vars))
                        result = BinOpNode(name, value, "=", lambda a, b: set_var(a, b, [readonly_flag,
                                                                                         indestructible_flag,
                                                                                         hidden_flag]))
                        return result
                    elif previous.pseudo_type == PT_INDEX_ASSIGNMENT:
                        name: str = previous.val
                        bracketized: List[Token] = prep_unary(raw[i + 1 - count:])
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        value = calculate(parse(bracketized, extra_vars=extra_vars))
                        result = BinOpNode(name, value, "=", lambda a, b: index_set_var(a, b, previous.extra_params))
                        return result
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            else:
                PyscriptSyntaxError("Invalid Syntax", True)
        elif token.type == TT_KEYWORD:
            if token.val == KW_READONLY:
                if i < len(tokenized) - 1:
                    readonly_flag = True
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_CONTINUE:
                return None, KW_CONTINUE
            if token.val == KW_BREAK:
                return None, KW_BREAK
            if token.val == KW_LABEL:
                if tokenized[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'label'", True)
                if next_token is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if next_token.type == TT_VAR:
                    return Label(next_token.val, 0, "")
                PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_DEF_LABEL:
                if tokenized[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'def_label'", True)
                if next_token is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if next_token.type == TT_VAR:
                    return Label(next_token.val, 0, "", True)
                PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_JUMP:
                if next_token is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if next_token.type == TT_VAR:
                    if not find_label(next_token.val).is_null:
                        return None, KW_JUMP, find_label(next_token.val)
                    PyscriptNameError(f"Label {next_token.val} does not exist", True)
                PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_CALL:
                if next_token is None:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if next_token.type == TT_VAR:
                    if not find_label(next_token.val).is_null:
                        return None, KW_CALL, find_label(next_token.val)
                    PyscriptNameError(f"Label {next_token.val} does not exist", True)
                PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_USING:
                if tokenized[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'using'", True)
                var_names: List[str] = []
                for section in split_list_by_token(TT_COMMA, TT_COMMA, raw[i + 1 - count:len(raw) - 1]):
                    if section[0].pseudo_type not in [PT_USING_REFERENCE, PT_USING_ASSIGN]:
                        PyscriptSyntaxError("Invalid Syntax/Unassigned variable in 'using' context", True)
                    var_names.append(section[0].val)
                    if section[0].pseudo_type == PT_USING_REFERENCE:
                        continue
                    bracketized: List[Token] = prep_unary(section)
                    bracketized, unused = bracketize(bracketized)
                    bracketized = unwrap_unary(bracketized)
                    calculate(parse(bracketized))
                return None, KW_USING, var_names
            if token.val == KW_DEL:
                var_names: List[str] = []
                for section in split_list_by_token(TT_COMMA, TT_COMMA, raw[i + 1 - count:]):
                    if section[0].pseudo_type != PT_DEL:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    var_names.append(section[0].val)
                return None, KW_DEL, var_names
            if token.val == KW_LOCAL:
                return None, KW_LOCAL
            if token.val == KW_OUT:
                var_names: List[str] = []
                for section in split_list_by_token(TT_COMMA, TT_COMMA, raw[i + 1 - count:]):
                    if section[0].pseudo_type != PT_OUT:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    var_names.append(section[0].val)
                return None, KW_OUT, var_names
            if token.val == KW_FOR:
                if raw[-1].val != TT_RANGE_TO:
                    PyscriptSyntaxError("Missing colon after 'for' loop", True)
                sections: List[List[Token]] = split_list_by_token(TT_SEMICOLON, TT_SEMICOLON,
                                                                  raw[i + 1 - count:len(raw) - 1])
                if len(sections) != 3:
                    PyscriptSyntaxError("Invalid Syntax", True)
                assignment: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, sections[0])
                condition: List[Token] = sections[1]
                update: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, sections[2])
                if len(assignment[0]) > 0:
                    for expr in assignment:
                        bracketized: List[Token] = prep_unary(expr)
                        bracketized, unused = bracketize(bracketized)
                        bracketized = unwrap_unary(bracketized)
                        calculate(parse(bracketized))
                if len(condition) == 0:
                    start = True
                else:
                    bracketized: List[Token] = prep_unary(condition)
                    bracketized, unused = bracketize(bracketized)
                    bracketized = unwrap_unary(bracketized)
                    start = calculate(parse(bracketized))
                if start:
                    return None, KW_FOR, condition, update
            if token.val == KW_FUNC:
                if raw[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon after 'func' definition", True)
                definition: List[Token] = raw[i + 1 - count:len(raw) - 1]
                decorators: List[Token] = raw[:i]
                is_inline: bool = False
                is_hidden: bool = False
                for decorator in decorators:
                    if decorator.val == KW_INLINE:
                        is_inline = True
                    elif decorator.val == KW_HIDDEN:
                        is_hidden = True
                sections: List[List[Token]] = split_list_by_token(TT_INSERTION, TT_INSERTION, definition)
                argument_section: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, sections[0])
                name: List[Token] = sections[1]
                if len(name) != 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                func: Variable = create_var(name[0].val, 0, [True, True, is_hidden], True)[-1]
                args = []
                for var in argument_section:
                    if len(var) == 0 and len(argument_section) == 1:
                        break
                    if len(var) != 1:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    args.append(var[0].val)
                un_ops.add(func.name)
                funcs.add(func.name)
                return None, KW_FUNC, func, args, is_inline
            if token.val == KW_EXTERN:
                definition: List[Token] = raw[i + 1 - count:]
                splitted_a: List[List[Token]] = split_list_by_token(TT_KEYWORD, KW_FUNC, definition)
                if len(splitted_a) != 2:
                    PyscriptSyntaxError("Invalid Syntax", True)
                ext_file: List[Token] = splitted_a[0]
                if len(ext_file) != 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                file_name: str = ext_file[0].val
                if type(file_name) != str:
                    PyscriptSyntaxError("Invalid Syntax", True)
                sections: List[List[Token]] = split_list_by_token(TT_INSERTION, TT_INSERTION, splitted_a[1])
                argument_section: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, sections[0])
                name: List[Token] = sections[1]
                r_value = None
                if len(sections) == 3:
                    r_value = sections[2]
                if len(name) != 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                args = []
                for var in argument_section:
                    if len(var) != 1:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    args.append(var[0].val)
                un_ops.add(name[0].val)
                funcs.add(name[0].val)
                return None, KW_EXTERN, name[0].val, args, file_name, r_value
            if token.val == KW_RETURN:
                bracketized: List[Token] = prep_unary(raw[i+1-count:])
                bracketized, unused = bracketize(bracketized)
                bracketized = unwrap_unary(bracketized)
                r_value = calculate(parse(bracketized))
                return None, KW_RETURN, r_value
            if token.val == KW_IMPORT:
                statement: List[List[Token]] = split_list_by_token(TT_KEYWORD, KW_AS, raw[i+1-count:])
                from_statement: List[List[Token]] = split_list_by_token(TT_KEYWORD, KW_FROM, raw[i+1-count:])
                alias: str = ""
                if len(statement) > 1:
                    if len(statement[1]) != 1 or len(from_statement) > 1:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    alias = statement[1][0].val
                things_to_import = []
                if len(from_statement) > 1:
                    statement[0] = from_statement[1]
                    statement.append(from_statement[0])
                    things_to_import: List[List[Token]] = split_list_by_token(TT_COMMA, TT_COMMA, statement[1])
                    for i, tokenized_things in enumerate(things_to_import):
                        if len(tokenized_things) != 1:
                            PyscriptSyntaxError("Invalid Syntax", True)
                        if tokenized_things[0].type != TT_VAR:
                            if tokenized_things[0].val == TT_MUL:
                                things_to_import = True
                            else:
                                PyscriptSyntaxError("Invalid Syntax", True)
                        if type(things_to_import) == list:
                            things_to_import[i] = tokenized_things[0].val
                return None, KW_IMPORT, make_path(statement[0]), alias, things_to_import
            if token.val == KW_INDESTRUCTIBLE:
                if i < len(tokenized) - 1:
                    indestructible_flag = True
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_LET:
                if i >= len(tokenized):
                    PyscriptSyntaxError("Invalid Syntax", True)
                splitted: List[List[Token]] = split_list_by_token(TT_KEYWORD, KW_BE, raw[i+1-count:], -1)
                if len(splitted) != 2:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if len(splitted[1]) != 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                definition = splitted[0]
                name = splitted[1][0]
                if name.type != TT_VAR:
                    PyscriptSyntaxError("Invalid Syntax", True)
                return TokDef(name.val, definition)
            if token.val == KW_REM_KW:
                if i >= len(tokenized)-1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                kw_to_remove = raw[i+1-count:]
                if len(kw_to_remove) != 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                tok_def: TokDef = TokDef.FindTokDef(kw_to_remove[0].val)
                if tok_def is None:
                    if kw_to_remove[0].val not in KEYWORDS.keys():
                        PyscriptSyntaxError("Invalid Syntax", True)

                    del KEYWORDS[kw_to_remove[0].val]
                    return ValueNode(0)
                tok_def.destroy()

                return ValueNode(1)
            if token.val == KW_SWITCH:
                if i >= len(tokenized) - 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if raw[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'switch' statement", True)
                pre_parse(raw, extra_vars)
                switch_value = calculate(parse(raw[i+1-count:len(raw)-1]))
                return None, KW_SWITCH, switch_value
            if token.val == KW_CASE:
                if i >= len(tokenized) - 1:
                    PyscriptSyntaxError("Invalid Syntax", True)
                if raw[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'case' statement", True)
                pre_parse(raw, extra_vars)
                return None, KW_CASE, calculate(parse(raw[i+1-count:len(raw)-1]))
            if token.val == KW_HIDDEN:
                if i < len(tokenized) - 1:
                    hidden_flag = True
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
            if token.val == KW_ASSERT:
                if i < len(tokenized) - 1:
                    pre_parse(raw)
                    result = calculate(parse(raw[i+1-count:]))
                    if type(result) != bool:
                        PyscriptSyntaxError("Invalid Syntax", True)
                    if not result:
                        PyscriptAssertionError(True)
                    return ValueNode(0)
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
        elif token.type == TT_BRANCH:
            if token.val == KW_IF:
                if tokenized[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'if' statement", True)
                bracketized: List[Token] = prep_unary(raw[i + 1 - count:])
                bracketized, unused = bracketize(bracketized)
                bracketized = unwrap_unary(bracketized)
                condition: bool = calculate(parse(bracketized))
                if type(condition) != bool:
                    PyscriptSyntaxError("Invalid Syntax", True)
                else:
                    return condition, TT_BRANCH
        elif token.type == TT_WHILE:
            bracketized: List[Token] = prep_unary(raw[i + 1 - count:])
            bracketized, unused = bracketize(bracketized)
            bracketized = unwrap_unary(bracketized)
            condition: bool = calculate(parse(bracketized))
            if type(condition) != bool:
                PyscriptSyntaxError("Invalid Syntax", True)
            else:
                if tokenized[-1].type != TT_COLON_END:
                    PyscriptSyntaxError("Missing colon at end of 'while' loop", True)
                return condition, TT_WHILE
        elif token.type == TT_PERIOD:
            if next_token.type == TT_VAR:
                if type(previous.val) != Variable:
                    var: Variable = get_var(previous.val)
                else:
                    var: Variable = previous.val
                accessed: Variable = None
                item_to_search: str = next_token.val
                for loc_var in var.extra_args:
                    if loc_var == item_to_search:
                        accessed = loc_var
                        break
                if accessed is not None:
                    if tokenized[i+1].pseudo_type != PT_ACCESSED:
                        tokenized[i+1].type = TT_INT
                        tokenized[i+1].val = accessed.value
                        tokenized[i+1].pseudo_type = None
                    else:
                        tokenized[i + 1].type = TT_INT
                        tokenized[i + 1].val = accessed
                        tokenized[i + 1].pseudo_type = None
                    del tokenized[i-1:i+1]
                    return parse(tokenized)
            elif next_token.type is None:
                funcs.add(next_token.val)
                var: Variable = get_var(previous.val)
                accessed: Variable = None
                item_to_search: str = next_token.val
                for loc_var in var.extra_args:
                    if loc_var == item_to_search:
                        accessed = loc_var
                        break
                if accessed is not None:
                    create_var("0"+accessed.name, 0, [True, True], True, accessed.extra_args, accessed.run_func,
                               accessed.r_value)
                    imported = True
                    imported_var = "0"+accessed.name
                else:
                    PyscriptSyntaxError("Invalid Syntax", True)
        elif token.pseudo_type == PT_CALLED:
            if token.val not in funcs:
                PyscriptSyntaxError(f"Variable {token.val} is not callable", True)
        i += 1
    return result


def calculate(node: Node):
    try:
        return node.get_value()
    except AttributeError:
        PyscriptSyntaxError("Invalid Syntax", True)
