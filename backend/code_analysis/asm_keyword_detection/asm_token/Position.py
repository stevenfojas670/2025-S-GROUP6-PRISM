"""
Created by Daniel Levy, 4/21/2025

This is a simple class designed to represent a position. A position
will be denoted by a line and a column, and we will use these positions
to keep track of where each token is located in relation to the file.
"""
class Position:
    __line = None   # Line Placement
    __col = None    # Column Placement

    def __init__(self,startLine=0,startCol=0):
        self.__line = startLine
        self.__col = startCol

    def getLine(self):
        return self.__line

    def getCol(self):
        return self.__col

    def toString(self):
        return f"<{self.__line}.{self.__col}>"
