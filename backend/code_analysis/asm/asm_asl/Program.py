
from code_analysis.asm.asm_asl.ASL import ASL

class Program(ASL):
    __init_data = None
    __uninit_data = None
    __code = None

    def __init__(self, startPos, endPos, init, uninit, code):
        super().__init__(startPos, endPos)
        self.__init_data = init
        self.__uninit_data = uninit
        self.__code = code

    def toString(self):
        for v in self.__init_data:
            print(v.toString())
