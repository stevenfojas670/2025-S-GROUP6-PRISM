
from enum import Enum

class TokenType(Enum):
    EOF = "$"
    ERROR = "ERROR"

    INSTR = "INSTR"
    DIRECTIVE = "DIRECTIVE"
    ID = "ID"
    NUM = "NUM"

    # OPERATORS
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIVIDE = "/"
    MOD = "%"
    OR = "|"
    AND = "&"
    XOR = "^"

    # DELIMITERS
    PERIOD = "."
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "["
    RBRACE = "]"
    COLON = ":"
    QUOTE = "'"
    DOLLAR = "$"

