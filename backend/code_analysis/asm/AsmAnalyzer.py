
import os
from code_analysis.asm.asm_lexer.Lexer import Lexer
from code_analysis.asm.asm_token.TokenType import TokenType

class AsmAnalyzer:

    __words = None
    __subDir = None
    __assignment = None
    __tokens = None
    __students:dict = None

    def __init__(self, words, submissionDir, assignment):
        self.__words = words
        self.__subDir = submissionDir
        self.__assignment = assignment
        self.__students = dict(dict(dict()))

    def tokenizeAssembly(self):
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

            self.__checkTokens(f.split('-')[1].strip())
        return self.__students

    def __checkTokens(self, studentName):
        for t in self.__tokens:
            for w in self.__words:
                if t.getLexeme() == w:
                    if not studentName in self.__students :
                        self.__students[studentName] = {"totalFound":0,"wordsFound":dict(dict())}
                    if not w in self.__students[studentName]["wordsFound"]:
                        self.__students[studentName]["wordsFound"][w] = {"count":0,"positions":list()}

                    self.__students[studentName]["wordsFound"][w]["count"] += 1
                    self.__students[studentName]["wordsFound"][w]["positions"].append(t.getStartPos().toString())
