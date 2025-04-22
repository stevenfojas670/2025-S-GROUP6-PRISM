
import os
from code_analysis.asm_keyword_detection.asm_lexer.Lexer import Lexer
from code_analysis.asm_keyword_detection.asm_token.Token import Token
from code_analysis.asm_keyword_detection.asm_token.TokenType import TokenType

class AsmAnalyzer:

    __words = None
    __oFile = None
    __subDir = None
    __assignment = None
    __tokens = None

    def __init__(self, words, oFile, submissionDir, assignment):
        self.__words = words
        self.__oFile = oFile
        self.__subDir = submissionDir
        self.__assignment = assignment
        self.__tokenizeAssembly()

    def __tokenizeAssembly(self):
        for f in os.listdir(self.__subDir):
            with open(f"{self.__subDir}/{f}/as{self.__assignment}.asm",'r') as submission:
                lexer = Lexer(submission.read())
                self.__tokens = list()
                while True:
                    currToken = lexer.nextToken()
                    self.__tokens.append(currToken)

                    if currToken.getType() == TokenType.EOF:
                        break
                    elif currToken.getType() == TokenType.ERROR:
                        break
            self.__checkTokens()

    def __checkTokens(self):
        for t in self.__tokens:
            for w in self.__words:
                if t.getLexeme() == w:
                    print("Found bad word!")
