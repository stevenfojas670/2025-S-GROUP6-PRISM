
from code_analysis.asm.asm_token.Token import Token
from code_analysis.asm.asm_token.TokenType import TokenType

class Parser:
    __tokens = None
    __currPos = None
    __lookahead = None

    def __init__(self, tokens):
        self.__tokens = tokens
        self.__currPos = 0
        self.__lookahead:Token = tokens[0]

    def __consume(self):
        self.__currPos += 1
        self.__lookahead = self.__tokens[self.__currPos]

    def __match(self, expected:TokenType):
        if self.__lookahead.getType() == expected:
            self.__consume()
            return True
        else:
            return False

    def __peek(self, expected:TokenType):
        return self.__lookahead.getType() == expected

    def __peekNext(self, expected:TokenType):
        if self.__currPos < len(self.__tokens) - 1:
            return self.__tokens[self.__currPos + 1].getType() == expected
        else:
            return False

    def __isRegister(self):


    # 1. <program> := <data>? <bss>? <text> ;
    def program(self):
        if self.__peek(TokenType.SECTION) and self.__peekNext(TokenType.ID_DATA):
            self.__data()
        elif self.__peek(TokenType.SECTION) and self.__peekNext(TokenType.ID_BSS):
            self.__bss()
        self.__text()

    # 2. <data> := 'section' '.data' <decl>* ;
    def __data(self):
        self.__match(TokenType.SECTION)
        self.__match(TokenType.ID_DATA)
        while self.__peek(TokenType.ID):
            self.__decl()

    # 3. <decl> := <ID> ('equ' | 'db' | 'dw' | 'dd' | 'dq') <number> ;
    def __decl(self):
        self.__match(TokenType.ID)
        if self.__peek(TokenType.EQU):
            self.__match(TokenType.EQU)
        else:
            if self.__peek(TokenType.DB): self.__match(TokenType.DB)
            elif self.__peek(TokenType.DW): self.__match(TokenType.DW)
            elif self.__peek(TokenType.DD): self.__match(TokenType.DD)
            elif self.__peek(TokenType.DQ): self.__match(TokenType.DQ)
            else: print("Error!")

        self.__match(TokenType.NUM)

    # 4. <bss> := 'section' '.bss' <unit_decl>* ;
    def __bss(self):
        self.__match(TokenType.SECTION)
        self.__match(TokenType.ID_BSS)
        while self.__peek(TokenType.ID):
            self.__unitDecl()

    # 5. <unit_decl> := <ID> ('resb' | 'resw' | 'resd' | 'resq') <number> ;
    def __unitDecl(self):
        self.__match(TokenType.ID)
        if self.__peek(TokenType.RESB): self.__match(TokenType.RESB)
        elif self.__peek(TokenType.RESW): self.__match(TokenType.RESW)
        elif self.__peek(TokenType.RESD): self.__match(TokenType.RESD)
        elif self.__peek(TokenType.RESQ): self.__match(TokenType.RESQ)
        else: print("Error!")
        self.__match(TokenType.NUM)

    # 6. <text> := 'section' '.text' 'global' '_start' '_start:' <code> ;
    def __text(self):
        self.__match(TokenType.SECTION)
        self.__match(TokenType.ID_TEXT)
        self.__match(TokenType.GLOBAL)
        self.__match(TokenType.START)
        self.__match(TokenType.ID)
        self.__code()

    # 7. <code> := ( <func_decl> (<label> | <instr>)* )* ;
    def __code(self):
        if self.__peek(TokenType.GLOBAL):
            self.__funcDecl()

        while not self.__peek(TokenType.EOF):
            if self.__peek(TokenType.ID):
                self.__label()
            else:
                self.__instr()

    # 8. <func_decl> := 'global' <ID> <label> ;
    def __funcDecl(self):
        self.__match(TokenType.GLOBAL)
        self.__match(TokenType.ID)
        self.__label()

    # 9. <label> := <ID> ;
    def __label(self):
        self.__match(TokenType.ID)

    # 10. <instr> := <instr_keyword> (<instr_info>)? ;
    def __instr(self):
        self.__consume()
        if(self.__peek(TokenType.BYTE)
                or self.__peek(TokenType.WORD)
                or self.__peek(TokenType.DWORD)
                or self.__peek(TokenType.QWORD))

    # 11. < instr_info > := (< reg_keyword > | < data_size >) *;
    #

    # 12. <data_size> := <size_keyword> '[' ( '(' | ')' | '+' | '*' | <reg_keyword> | <number> )+ ']' ;
    def __dataSize(self):
        if self.__peek(TokenType.BYTE): self.__match(TokenType.BYTE)
        elif self.__peek(TokenType.WORD): self.__match(TokenType.WORD)
        elif self.__peek(TokenType.DWORD): self.__match(TokenType.DWORD)
        elif self.__peek(TokenType.QWORD): self.__match(TokenType.QWORD)
        else: print("ERROR")

        self.__match(TokenType.LBRACK)
        while not self.__peek(TokenType.RBRACK):
            if self.__peek(TokenType.LPAREN): self.__match(TokenType.LPAREN)
            elif self.__peek(TokenType.RPAREN): self.__match(TokenType.RPAREN)
            elif self.__peek(TokenType.PLUS): self.__match(TokenType.PLUS)
            elif self.__peek(TokenType.MUL): self.__match(TokenType.MUL)
            elif self.__peek(TokenType.NUM): self.__match(TokenType.NUM)
            else: self.__consume()
        self.__match(TokenType.RBRACK)


