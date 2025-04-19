
class KeywordToken:
    # Fields
    __type = None
    __lineNum = None
    __lexeme = None

    def __init__(self,type,lineNum,lexeme):
        self.__type = type
        self.__lineNum = lineNum
        self.__lexeme = lexeme

    def getType(self):
        return self.__type

    def printToken(self):
        print(f"{self.__type.name}:{self.__lexeme} @ Line {self.__lineNum}")
