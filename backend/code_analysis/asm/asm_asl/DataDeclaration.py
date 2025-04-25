
from code_analysis.asm.asm_asl.ASL import ASL

class DataDeclaration(ASL):
    __name:str = None
    __size:str = None
    __value = None

    __isConstant:bool = None

    def __init__(self, startPos, endPos, name, size, value, constant):
        super.__init__(startPos, endPos)
        self.__name = name
        self.__size = size
        self.__value = value
        self.__isConstant = constant
