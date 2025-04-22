
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

    def __tokenizeString(self):
        startPos = self.__createPosition()
        string = "\""
        self.__match('\"')

        while not self.__match('\"') and not self.__match(self.__EOF):
            string += self.__lookahead
            self.__consume()

        string += "\""
        return Token(TokenType.STR,string,startPos,self.__createPosition())


    def __tokenizeNumber(self):
        startPos = self.__createPosition()
        number = ""
        while self.__lookahead.isdigit():
            number += self.__lookahead
            self.__consume()
            if self.__lookahead == '.':
                number += self.__lookahead
                self.__consume()

        return Token(TokenType.NUM,number,startPos,self.__createPosition())

    def __tokenizeName(self):
        startPos = self.__createPosition()
        id = ""
        while self.__lookahead.isalpha() or self.__lookahead.isdigit():
            id += self.__lookahead
            self.__consume()

        match id:
            case 'mov': return Token(TokenType.MOV,id,startPos,self.__createPosition())
            case 'lea': return Token(TokenType.LEA,id,startPos,self.__createPosition())



    def nextToken(self):
        while self.__lookahead != self.__EOF:
            startPos = self.__createPosition()
            match self.__lookahead:
                case '\n':
                    self.__consumeNewLine()
                case ' ' | '\t' | '\r':
                    self.__consumeWhiteSpace()
                case '+':
                    self.__match('+')
                    return Token(TokenType.PLUS,"+",startPos,self.__createPosition())
                case '-':
                    self.__match('-')
                    return Token(TokenType.MINUS,"-",startPos,self.__createPosition())
                case '*':
                    self.__match('*')
                    return Token(TokenType.MULT,"*",startPos,self.__createPosition())
                case '/':
                    self.__match('/')
                    return Token(TokenType.DIV,"/",startPos,self.__createPosition())
                case '%':
                    self.__match('%')
                    return Token(TokenType.MOD,"%",startPos,self.__createPosition())
                case '|':
                    self.__match('|')
                    return Token(TokenType.OR,"|",startPos,self.__createPosition())
                case '&':
                    self.__match('&')
                    return Token(TokenType.AND,"&",startPos,self.__createPosition())
                case '.':
                    self.__match('.')
                    return Token(TokenType.PERIOD,".",startPos,self.__createPosition())
                case ',':
                    self.__match(',')
                    return Token(TokenType.COMMA,",",startPos,self.__createPosition())
                case '(':
                    self.__match('(')
                    return Token(TokenType.LPAREN,"(",startPos,self.__createPosition())
                case ')':
                    self.__match(')')
                    return Token(TokenType.RPAREN,")",startPos,self.__createPosition())
                case '[':
                    self.__match('[')
                    return Token(TokenType.LBRACK,"[",startPos,self.__createPosition())
                case ']':
                    self.__match(']')
                    return Token(TokenType.RBRACK,"]",startPos,self.__createPosition())
                case ':':
                    self.__match(':')
                    return Token(TokenType.COLON,":",startPos,self.__createPosition())
                case '\'':
                    self.__match('\'')
                    return Token(TokenType.SQUOTE,"\'",startPos,self.__createPosition())
                case '\"':
                    return self.__tokenizeString()
                case _:
                    if self.__lookahead.isdigit():
                        return self.__tokenizeNumber()
                    elif self.__lookahead.isalpha():
                        return self.__tokenizeName()
                    else:
                        return Token(TokenType.ERROR,"ERROR!",startPos,self.__createPosition())

        return Token(TokenType.EOF,"$",self.__createPosition(),self.__createPosition())

def main():
    inputStr = 'mov mov lea lea mov lea'
    tokens = list()
    lexer = Lexer(inputStr)
    while True:
        currToken = lexer.nextToken()
        tokens.append(currToken)
        print(currToken.toString())

        if currToken.getType() == TokenType.EOF:
            break


if __name__ == "__main__":
    main()
