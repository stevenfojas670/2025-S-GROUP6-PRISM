
from code_analysis.asm_keyword_detection.asm_token import *

class Lexer:
    __EOF = '\0'
    __program:str = None
    __currPos:int = None
    __currLine:int = None
    __currCol:int = None

    def __init__(self, program):
        self.__program = program
        self.__currPos = 0
        self.__lookahead = program[0]
        self.__currLine = 1
        self.__currCol = 1

    def __consume(self):
        if self.__curPos != self.__EOF:
            self.__currPos += 1

    def __match(self,currChar):
        if(self.__program[self.__currPos] == currChar):
            return True
        return False

    def __nextToken(self):
        while self.__program[self.__currPos] != self.__EOF:
            pass
