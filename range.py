from errors import PyscriptSyntaxError


def range_from_to(start, stop):
    ranged = []
    if type(start) == int and type(stop) == int:
        i = start
        while i < stop:
            ranged.append(i)
            i += 1
    else:
        PyscriptSyntaxError("Invalid Syntax", True)
    return ranged
