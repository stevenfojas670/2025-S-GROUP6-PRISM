
import os
from code_analysis.asm_keyword_detection.asm_lexer.Lexer import Lexer
from code_analysis.asm_keyword_detection.asm_token.Token import Token
from code_analysis.asm_keyword_detection.asm_token.TokenType import TokenType

class AsmAnalyzer:

    __words = None
    __oFile = None
    __subDir = None
    __tokens = None

    def __init__(self, words, oFile, submissionDir):
        self.__words = words
        self.__oFile = oFile
        self.__subDir = submissionDir
        self.__tokenizeAssembly()

    def __tokenizeAssembly(self):
        for f in os.listdir(self.__subDir):
            with open(f,'r') as submission:
                lexer = Lexer(submission.readlines())
                self.__tokens = list()
                while True:
                    currToken = lexer.nextToken()
                    self.__tokens.append(currToken)

                    if currToken.getType() == TokenType.EOF:
                        break
                    elif currToken.getType() == TokenType.ERROR:
                        break
