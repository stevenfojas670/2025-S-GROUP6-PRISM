
from code_analysis.asm.asm_asl.ASL import ASL

class Program(ASL):
    __init_data = None
    __uninit_data = None
    __code = None

    def __init__(self, init):
        super.__init__(init)
        self.__init_data = init