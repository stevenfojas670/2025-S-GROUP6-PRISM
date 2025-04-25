
from code_analysis.asm.asm_asl.ASL import ASL

class Instruction(ASL):
    __instruction:str = None
    __extraInfo = None

    def __init__(self, startPos, endPos, instr, extra):
        super().__init__(startPos, endPos)
        self.__instruction = instr
        self.__extraInfo = extra

    def toString(self):
        return f"{self.__instruction}"