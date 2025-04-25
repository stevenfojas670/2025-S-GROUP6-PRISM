
from code_analysis.asm.asm_token.Token import Token
from code_analysis.asm.asm_token.TokenType import TokenType

class Parser:
    __tokens = None
    __currPos = None
    __lookahead = None

    def __init__(self, tokens):
        self.__tokens = tokens
        self.__currPos = 0
        self.__lookahead:Token = tokens[0]

    def __consume(self):
        self.__currPos += 1
        self.__lookahead = self.__tokens[self.__currPos]

    def __match(self,expected:TokenType):
        if self.__lookahead.getType() == expected:
            self.__consume()
            return True
        else:
            return False

    def __nextLA(self):
        if self.__currPos < len(self.__tokens) - 1:
            return self.__tokens[self.__currPos+1].getType()
        else:
            return None


