
from code_analysis.asm.asm_asl.ASL import ASL

class UnitDeclaration(ASL):
    __name:str = None
    __size:str = None
    __values = None

    def __init__(self, startPos, endPos, name, size, values):
        super().__init__(startPos, endPos)
        self.__name = name
        self.__size = size
        self.__values = values

    def toString(self):
        return f"{self.__name}"
