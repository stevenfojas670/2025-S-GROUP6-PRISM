
from code_analysis.asm.asm_asl.ASL import ASL

class DataSize(ASL):
    __size = None
    __lst = None

    def __init__(self, startPos, endPos, size, lst):
        super().__init__(startPos, endPos)
        self.__size = size
        self.__lst = lst

    def toString(self):
        return f"{self.__size}"
        