
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
