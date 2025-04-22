
from code_analysis.asm_keyword_detection.asm_token import *

class Lexer:
    __EOF:str = '\0'
    __program:str = None
    __currPos:int = None
    __lookahead:str = None
    __currLine:int = None
    __currCol:int = None

    def __init__(self, program):
        self.__program = program
        self.__currPos = 0
        self.__lookahead = program[0]
        self.__currLine = 1
        self.__currCol = 1

    def __consume(self):
        if self.__lookahead != self.__EOF:
            self.__currPos += 1
            self.__lookahead = self.__program[self.__currPos]
            self.__curCol += 1

    def __match(self,currChar):
        if(self.__lookahead  == currChar):
            return True
        return False

    def __consumeNewLine(self):
        self.__consume()
        self.__currLine += 1
        self.__currCol = 1

    def __consumeWhiteSpace(self):
        while self.__lookahead != [' ', '\t', '\r']:
            self.__consume()

    def __nextToken(self):
        while self.__lookahead != self.__EOF:
            match self.__lookahead:
                case '\n':
                    self.__consumeNewLine()
                case [' ','\t','\r']:
                    self.__consumeWhiteSpace()
            pass
