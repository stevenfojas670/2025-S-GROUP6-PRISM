
from code_analysis.asm_keyword_detection.asm_token.Position import Position
from code_analysis.asm_keyword_detection.asm_token.Token import Token
from code_analysis.asm_keyword_detection.asm_token.TokenType import TokenType

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
        self.__currPos += 1
        self.__currCol += 1

        if self.__currPos < len(self.__program):
            self.__lookahead = self.__program[self.__currPos]
        else:
            self.__lookahead = self.__EOF

    def __match(self,currChar):
        if(self.__lookahead  == currChar):
            self.__consume()
            return True
        return False

    def __consumeNewLine(self):
        self.__consume()
        self.__currLine += 1
        self.__currCol = 1

    def __consumeWhiteSpace(self):
        while self.__lookahead == ' ' \
           or self.__lookahead == '\t' \
           or self.__lookahead == '\r':
            self.__consume()

    def __createPosition(self):
        return Position(self.__currLine,self.__currCol)

    def nextToken(self):
        while self.__lookahead != self.__EOF:
            startPos = self.__createPosition()
            match self.__lookahead:
                case '\n':
                    self.__consumeNewLine()
                case [' ','\t','\r']:
                    self.__consumeWhiteSpace()
                case '+':
                    self.__match('+')
                    return Token(TokenType.PLUS,"+",startPos,self.__createPosition())

        return Token(TokenType.EOF,"$",self.__createPosition(),self.__createPosition())

def main():
    inputStr = "++"
    tokens = list()
    lexer = Lexer(inputStr)
    while True:
        currToken = lexer.nextToken()
        tokens.append(currToken)
        if currToken.getType() == TokenType.EOF:
            break

        print(currToken.toString())

if __name__ == "__main__":
    main()
