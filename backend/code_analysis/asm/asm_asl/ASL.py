
from code_analysis.asm.asm_token.Position import Position

class ASL:
    __startPos:Position = None
    __endPos:Position = None

    def __init__(self, start, end):
        self.__startPos = start
        self.__endPos = end

    def getStartPos(self):
        return self.__startPos

    def getEndPos(self):
        return self.__endPos
