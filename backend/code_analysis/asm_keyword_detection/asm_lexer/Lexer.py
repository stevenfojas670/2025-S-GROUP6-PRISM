
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

    def __consumeComment(self):
        self.__consume()
        while self.__lookahead != '\n':
            self.__consume()
        self.__consumeNewLine()

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
        while (self.__lookahead.isalpha()
            or self.__lookahead.isdigit()
            or self.__lookahead == "%"
            or self.__lookahead == "_"
            or self.__lookahead == "."):
            id += self.__lookahead
            self.__consume()

        match id:
            case 'rax': return Token(TokenType.RAX, id, startPos, self.__createPosition())
            case 'eax': return Token(TokenType.EAX, id, startPos, self.__createPosition())
            case 'ax': return Token(TokenType.AX, id, startPos, self.__createPosition())
            case 'al': return Token(TokenType.AL, id, startPos, self.__createPosition())
            case 'rbx': return Token(TokenType.RBX, id, startPos, self.__createPosition())
            case 'ebx': return Token(TokenType.EBX, id, startPos, self.__createPosition())
            case 'bx': return Token(TokenType.BX, id, startPos, self.__createPosition())
            case 'bl': return Token(TokenType.BL, id, startPos, self.__createPosition())
            case 'rcx': return Token(TokenType.RCX, id, startPos, self.__createPosition())
            case 'ecx': return Token(TokenType.ECX, id, startPos, self.__createPosition())
            case 'cx': return Token(TokenType.CX, id, startPos, self.__createPosition())
            case 'cl': return Token(TokenType.CL, id, startPos, self.__createPosition())
            case 'rdx': return Token(TokenType.RDX, id, startPos, self.__createPosition())
            case 'edx': return Token(TokenType.EDX, id, startPos, self.__createPosition())
            case 'dx': return Token(TokenType.DX, id, startPos, self.__createPosition())
            case 'dl': return Token(TokenType.DL, id, startPos, self.__createPosition())
            case 'rsi': return Token(TokenType.RSI, id, startPos, self.__createPosition())
            case 'esi': return Token(TokenType.ESI, id, startPos, self.__createPosition())
            case 'si': return Token(TokenType.SI, id, startPos, self.__createPosition())
            case 'sil': return Token(TokenType.SIL, id, startPos, self.__createPosition())
            case 'rdi': return Token(TokenType.RDI, id, startPos, self.__createPosition())
            case 'edi': return Token(TokenType.EDI, id, startPos, self.__createPosition())
            case 'di': return Token(TokenType.DI, id, startPos, self.__createPosition())
            case 'dil': return Token(TokenType.DIL, id, startPos, self.__createPosition())
            case 'rbp': return Token(TokenType.RBP, id, startPos, self.__createPosition())
            case 'ebp': return Token(TokenType.EBP, id, startPos, self.__createPosition())
            case 'bp': return Token(TokenType.BP, id, startPos, self.__createPosition())
            case 'bpl': return Token(TokenType.BPL, id, startPos, self.__createPosition())
            case 'rsp': return Token(TokenType.RSP, id, startPos, self.__createPosition())
            case 'esp': return Token(TokenType.ESP, id, startPos, self.__createPosition())
            case 'sp': return Token(TokenType.SP, id, startPos, self.__createPosition())
            case 'spl': return Token(TokenType.SPL, id, startPos, self.__createPosition())
            case 'r8': return Token(TokenType.R8, id, startPos, self.__createPosition())
            case 'r8d': return Token(TokenType.R8D, id, startPos, self.__createPosition())
            case 'r8w': return Token(TokenType.R8W, id, startPos, self.__createPosition())
            case 'r8b': return Token(TokenType.R8B, id, startPos, self.__createPosition())
            case 'r9': return Token(TokenType.R9, id, startPos, self.__createPosition())
            case 'r9d': return Token(TokenType.R9D, id, startPos, self.__createPosition())
            case 'r9w': return Token(TokenType.R9W, id, startPos, self.__createPosition())
            case 'r9b': return Token(TokenType.R9B, id, startPos, self.__createPosition())
            case 'r10': return Token(TokenType.R10, id, startPos, self.__createPosition())
            case 'r10d': return Token(TokenType.R10D, id, startPos, self.__createPosition())
            case 'r10w': return Token(TokenType.R10W, id, startPos, self.__createPosition())
            case 'r10b': return Token(TokenType.R10B, id, startPos, self.__createPosition())
            case 'r11': return Token(TokenType.R11, id, startPos, self.__createPosition())
            case 'r11d': return Token(TokenType.R11D, id, startPos, self.__createPosition())
            case 'r11w': return Token(TokenType.R11W, id, startPos, self.__createPosition())
            case 'r11b': return Token(TokenType.R11B, id, startPos, self.__createPosition())
            case 'r12': return Token(TokenType.R12, id, startPos, self.__createPosition())
            case 'r12d': return Token(TokenType.R12D, id, startPos, self.__createPosition())
            case 'r12w': return Token(TokenType.R12W, id, startPos, self.__createPosition())
            case 'r12b': return Token(TokenType.R12B, id, startPos, self.__createPosition())
            case 'r13': return Token(TokenType.R13, id, startPos, self.__createPosition())
            case 'r13d': return Token(TokenType.R13D, id, startPos, self.__createPosition())
            case 'r13w': return Token(TokenType.R13W, id, startPos, self.__createPosition())
            case 'r13b': return Token(TokenType.R13B, id, startPos, self.__createPosition())
            case 'r14': return Token(TokenType.R14, id, startPos, self.__createPosition())
            case 'r14d': return Token(TokenType.R14D, id, startPos, self.__createPosition())
            case 'r14w': return Token(TokenType.R14W, id, startPos, self.__createPosition())
            case 'r14b': return Token(TokenType.R14B, id, startPos, self.__createPosition())
            case 'r15': return Token(TokenType.R15, id, startPos, self.__createPosition())
            case 'r15d': return Token(TokenType.R15D, id, startPos, self.__createPosition())
            case 'r15w': return Token(TokenType.R15W, id, startPos, self.__createPosition())
            case 'r15b': return Token(TokenType.R15B, id, startPos, self.__createPosition())
            case 'xmm0': return Token(TokenType.XMM0, id, startPos, self.__createPosition())
            case 'xmm1': return Token(TokenType.XMM1, id, startPos, self.__createPosition())
            case 'xmm2': return Token(TokenType.XMM2, id, startPos, self.__createPosition())
            case 'xmm3': return Token(TokenType.XMM3, id, startPos, self.__createPosition())
            case 'xmm4': return Token(TokenType.XMM4, id, startPos, self.__createPosition())
            case 'xmm5': return Token(TokenType.XMM5, id, startPos, self.__createPosition())
            case 'xmm6': return Token(TokenType.XMM6, id, startPos, self.__createPosition())
            case 'xmm7': return Token(TokenType.XMM7, id, startPos, self.__createPosition())
            case 'xmm8': return Token(TokenType.XMM8, id, startPos, self.__createPosition())
            case 'xmm9': return Token(TokenType.XMM9, id, startPos, self.__createPosition())
            case 'xmm10': return Token(TokenType.XMM10, id, startPos, self.__createPosition())
            case 'xmm11': return Token(TokenType.XMM11, id, startPos, self.__createPosition())
            case 'xmm12': return Token(TokenType.XMM12, id, startPos, self.__createPosition())
            case 'xmm13': return Token(TokenType.XMM13, id, startPos, self.__createPosition())
            case 'xmm14': return Token(TokenType.XMM14, id, startPos, self.__createPosition())
            case 'xmm15': return Token(TokenType.XMM15, id, startPos, self.__createPosition())

            case 'equ': return Token(TokenType.EQU, id, startPos, self.__createPosition())
            case 'db': return Token(TokenType.DB, id, startPos, self.__createPosition())
            case 'dw': return Token(TokenType.DW, id, startPos, self.__createPosition())
            case 'dd': return Token(TokenType.DD, id, startPos, self.__createPosition())
            case 'dq': return Token(TokenType.DQ, id, startPos, self.__createPosition())
            case 'ddq': return Token(TokenType.DDQ, id, startPos, self.__createPosition())
            case 'dt': return Token(TokenType.DT, id, startPos, self.__createPosition())
            case 'resb': return Token(TokenType.RESB, id, startPos, self.__createPosition())
            case 'resw': return Token(TokenType.RESW, id, startPos, self.__createPosition())
            case 'resd': return Token(TokenType.RESD, id, startPos, self.__createPosition())
            case 'resq': return Token(TokenType.RESQ, id, startPos, self.__createPosition())
            case 'resdq': return Token(TokenType.RESDQ, id, startPos, self.__createPosition())
            case 'byte': return Token(TokenType.BYTE, id, startPos, self.__createPosition())
            case 'word': return Token(TokenType.WORD, id, startPos, self.__createPosition())
            case 'dword': return Token(TokenType.DWORD, id, startPos, self.__createPosition())
            case 'qword': return Token(TokenType.QWORD, id, startPos, self.__createPosition())
            case 'section': return Token(TokenType.SECTION, id, startPos, self.__createPosition())
            case 'global': return Token(TokenType.GLOBAL, id, startPos, self.__createPosition())
            case 'mov': return Token(TokenType.MOV, id, startPos, self.__createPosition())
            case 'lea': return Token(TokenType.LEA, id, startPos, self.__createPosition())
            case 'movzx': return Token(TokenType.MOVZX, id, startPos, self.__createPosition())
            case 'cbw': return Token(TokenType.CBW, id, startPos, self.__createPosition())
            case 'cwd': return Token(TokenType.CWD, id, startPos, self.__createPosition())
            case 'cwde': return Token(TokenType.CWDE, id, startPos, self.__createPosition())
            case 'cdq': return Token(TokenType.CDQ, id, startPos, self.__createPosition())
            case 'cdqe': return Token(TokenType.CDQE, id, startPos, self.__createPosition())
            case 'cqo': return Token(TokenType.CQO, id, startPos, self.__createPosition())
            case 'movsx': return Token(TokenType.MOVSX, id, startPos, self.__createPosition())
            case 'movsxd': return Token(TokenType.MOVSXD, id, startPos, self.__createPosition())
            case 'add': return Token(TokenType.ADD, id, startPos, self.__createPosition())
            case 'inc': return Token(TokenType.INC, id, startPos, self.__createPosition())
            case 'adc': return Token(TokenType.ADC, id, startPos, self.__createPosition())
            case 'sub': return Token(TokenType.SUB, id, startPos, self.__createPosition())
            case 'dec': return Token(TokenType.DEC, id, startPos, self.__createPosition())
            case 'mul': return Token(TokenType.MUL, id, startPos, self.__createPosition())
            case 'imul': return Token(TokenType.IMUL, id, startPos, self.__createPosition())
            case 'div': return Token(TokenType.DIV, id, startPos, self.__createPosition())
            case 'idiv': return Token(TokenType.IDIV, id, startPos, self.__createPosition())
            case 'and': return Token(TokenType.AND, id, startPos, self.__createPosition())
            case 'or': return Token(TokenType.OR, id, startPos, self.__createPosition())
            case 'xor': return Token(TokenType.XOR, id, startPos, self.__createPosition())
            case 'not': return Token(TokenType.NOT, id, startPos, self.__createPosition())
            case 'shl': return Token(TokenType.SHL, id, startPos, self.__createPosition())
            case 'shr': return Token(TokenType.SHR, id, startPos, self.__createPosition())
            case 'sal': return Token(TokenType.SAL, id, startPos, self.__createPosition())
            case 'sar': return Token(TokenType.SAR, id, startPos, self.__createPosition())
            case 'rol': return Token(TokenType.ROL, id, startPos, self.__createPosition())
            case 'ror': return Token(TokenType.ROR, id, startPos, self.__createPosition())
            case 'jmp': return Token(TokenType.JMP, id, startPos, self.__createPosition())
            case 'cmp': return Token(TokenType.CMP, id, startPos, self.__createPosition())
            case 'je': return Token(TokenType.JE, id, startPos, self.__createPosition())
            case 'jne': return Token(TokenType.JNE, id, startPos, self.__createPosition())
            case 'jl': return Token(TokenType.JL, id, startPos, self.__createPosition())
            case 'jle': return Token(TokenType.JLE, id, startPos, self.__createPosition())
            case 'jg': return Token(TokenType.JG, id, startPos, self.__createPosition())
            case 'jge': return Token(TokenType.JGE, id, startPos, self.__createPosition())
            case 'jb': return Token(TokenType.JB, id, startPos, self.__createPosition())
            case 'jbe': return Token(TokenType.JBE, id, startPos, self.__createPosition())
            case 'ja': return Token(TokenType.JA, id, startPos, self.__createPosition())
            case 'jae': return Token(TokenType.JAE, id, startPos, self.__createPosition())
            case 'loop': return Token(TokenType.LOOP, id, startPos, self.__createPosition())
            case 'push': return Token(TokenType.PUSH, id, startPos, self.__createPosition())
            case 'pop': return Token(TokenType.POP, id, startPos, self.__createPosition())
            case 'call': return Token(TokenType.CALL, id, startPos, self.__createPosition())
            case 'ret': return Token(TokenType.RET, id, startPos, self.__createPosition())
            case 'movss': return Token(TokenType.MOVSS, id, startPos, self.__createPosition())
            case 'movsd': return Token(TokenType.MOVSD, id, startPos, self.__createPosition())
            case 'cvtss2sd': return Token(TokenType.CVTSS2SD, id, startPos, self.__createPosition())
            case 'cvtsd2ss': return Token(TokenType.CVTSD2SS, id, startPos, self.__createPosition())
            case 'cvtss2si': return Token(TokenType.CVTSS2SI, id, startPos, self.__createPosition())
            case 'cvtsd2si': return Token(TokenType.CVTSD2SI, id, startPos, self.__createPosition())
            case 'cvtsi2ss': return Token(TokenType.CVTSI2SS, id, startPos, self.__createPosition())
            case 'cvtsi2sd': return Token(TokenType.CVTSI2SD, id, startPos, self.__createPosition())
            case 'addss': return Token(TokenType.ADDSS, id, startPos, self.__createPosition())
            case 'addsd': return Token(TokenType.ADDSD, id, startPos, self.__createPosition())
            case 'subss': return Token(TokenType.SUBSS, id, startPos, self.__createPosition())
            case 'subsd': return Token(TokenType.SUBSD, id, startPos, self.__createPosition())
            case 'mulss': return Token(TokenType.MULSS, id, startPos, self.__createPosition())
            case 'mulsd': return Token(TokenType.MULSD, id, startPos, self.__createPosition())
            case 'divss': return Token(TokenType.DIVSS, id, startPos, self.__createPosition())
            case 'divsd': return Token(TokenType.DIVSD, id, startPos, self.__createPosition())
            case 'sqrtss': return Token(TokenType.SQRTSS, id, startPos, self.__createPosition())
            case 'sqrtsd': return Token(TokenType.SQRTSD, id, startPos, self.__createPosition())
            case 'ucomiss': return Token(TokenType.UCOMIS, id, startPos, self.__createPosition())
            case 'ucomisd': return Token(TokenType.UCOMISD, id, startPos, self.__createPosition())
            case 'syscall': return Token(TokenType.SYSCALL, id, startPos, self.__createPosition())
            case 'cmovl': return Token(TokenType.CMOVL, id, startPos, self.__createPosition())
            case 'cmovg': return Token(TokenType.CMOVG, id, startPos, self.__createPosition())
            case 'asr': return Token(TokenType.ASR, id, startPos, self.__createPosition())
            case 'jnz': return Token(TokenType.JNZ, id, startPos, self.__createPosition())
            case 'rel': return Token(TokenType.REL, id, startPos, self.__createPosition())
            case '%define': return Token(TokenType.DEFINE, id, startPos, self.__createPosition())
            case _: return Token(TokenType.ID,id,startPos,self.__createPosition())


    def nextToken(self):
        while self.__lookahead != self.__EOF:
            startPos = self.__createPosition()
            match self.__lookahead:
                case ';':
                    self.__consumeComment()
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
                    return Token(TokenType.DIVIDE,"/",startPos,self.__createPosition())
                case '%':
                    self.__match('%')
                    return Token(TokenType.MOD,"%",startPos,self.__createPosition())
                case '|':
                    self.__match('|')
                    return Token(TokenType.BOR,"|",startPos,self.__createPosition())
                case '&':
                    self.__match('&')
                    return Token(TokenType.BAND,"&",startPos,self.__createPosition())
                case '.':
                    self.__match('.')
                    if(self.__lookahead.isalpha()):
                        self.__currPos -= 1
                        self.__lookahead = '.'
                        return self.__tokenizeName()
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
                    elif self.__lookahead.isalpha() or self.__lookahead == "%" or self.__lookahead == "_":
                        return self.__tokenizeName()
                    else:
                        return Token(TokenType.ERROR,"ERROR!",startPos,self.__createPosition())

        return Token(TokenType.EOF,"$",self.__createPosition(),self.__createPosition())

def main():
    inputStr = """"""
    tokens = list()
    lexer = Lexer(inputStr)
    while True:
        currToken = lexer.nextToken()
        tokens.append(currToken)
        print(currToken.toString())

        if currToken.getType() == TokenType.EOF:
            break
        elif currToken.getType() == TokenType.ERROR:
            break


if __name__ == "__main__":
    main()
