
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

    def __currentLA(self):
        return self.__lookahead.getType()

    def __nextLA(self):
        if self.__currPos < len(self.__tokens) - 1:
            return self.__tokens[self.__currPos+1].getType()
        else:
            return None

    # 1. <program> := <data>? <bss>? <text> ;
    def program(self):
        if self.__currentLA() == TokenType.SECTION and self.__nextLA() == TokenType.ID_DATA:
            self.__data()

    def __data(self):
        self.__match(TokenType.SECTION)
        self.__match(TokenType.ID_DATA)
        while self.__currentLA() == TokenType.ID:
            self.__decl()

    def __decl(self):
        self.__match(TokenType.ID)
        if self.__currentLA == TokenType.EQU:
            self.__match(TokenType.EQU)
            self.__match(TokenType.NUM)
        else:
            # if self.__current