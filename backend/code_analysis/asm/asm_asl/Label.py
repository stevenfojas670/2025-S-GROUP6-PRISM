
from code_analysis.asm.asm_asl.ASL import ASL
from code_analysis.asm.asm_token.Token import Token

class Label(ASL):
    __name:str = None

    def __init__(self, labelToken:Token):
        super().__init__(labelToken.getStartPos(),labelToken.getEndPos())
        self.__name = labelToken.getLexeme()

    def toString(self):
        return f"{self.__name}"
