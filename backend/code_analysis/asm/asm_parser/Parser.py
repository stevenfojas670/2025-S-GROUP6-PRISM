
class Parser:
    __tokens = None
    __currPos = None
    __lookahead = None

    def __init__(self, tokens):
        __tokens = tokens
        __currPos = 0
        __lookahead = tokens[0]
