
import os
from asm_lexer import Lexer

class AsmAnalyzer:

    __words = None
    __oFile = None

    def __init__(self,words,oFile):
        self.__words = words
        self.__oFile = oFile

