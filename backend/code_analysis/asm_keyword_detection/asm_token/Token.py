
from code_analysis.asm_keyword_detection.asm_token import Position
from code_analysis.asm_keyword_detection.asm_token.TokenType import TokenType

class Token:
    __type = None
    __lexeme = None
    __startPos = None
    __endPos = None

    def __init__(self, type:TokenType,lex:str,start:Position,end:Position):
        self.__type = type
        self.__lexeme = lex
        self.__startPos = start
        self.__endPos = end

    def getType(self):
        return self.__type

    def getLexeme(self):
        return self.__lexeme

    def getStartPos(self):
        return self.__startPos

    def getEndPos(self):
        return self.__endPos

    def toString(self):
        return (f"Type = {self.__type.name}, Lexeme = '{self.__lexeme}', "
                f"Location = {self.__startPos.toString()} to {self.__endPos.toString()}")