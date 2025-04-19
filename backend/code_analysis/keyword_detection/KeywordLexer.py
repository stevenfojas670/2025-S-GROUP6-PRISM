import KeywordToken
import KeywordTokenType

class KeywordLexer:
    # Fields
    __program = None
    __lookahead = None
    __lineNum = None

    # Methods
    def __init__(self,file):
        self.__program = file
        self.__lookahead = 0
        self.__lineNum = 1

    def __consume(self):
        if(self.__lookahead <= len(self.__program)):
            self.__lookahead += 1

    def __match(self,currChar):
        if(currChar == self.__program[self.__lookahead]):
            self.__consume()
            return True
        return False

    def __nextToken(self):
        pass