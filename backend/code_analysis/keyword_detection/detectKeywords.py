import sys
import os

from clang import cindex
from clang.cindex import CursorKind

class KeywordAnalyzer:
    __assignmentNum = None
    __words = None
    __jsonFile = None

    def __init__(self, inputFile):
        self.__words = list()
        self.__openAndValidateFile(inputFile)
        self.__createJSON()
        self.__runAnalysis()

    '''
        This method is responsible for opening the input file
        containing the banned keywords, storing them into the
        KeywordAnalyzer's words array, and also getting the 
        assignment for which the keyword analysis will be done for
    '''
    def __openAndValidateFile(self,iFile):
        # ERROR CHECK #1: Make sure the file exists in the
        #                 keyword_detection package
        if not os.path.exists(iFile):
            print("Error! Banned keyword file does not exist!")
            exit(1)

        file = open(iFile,'r')

        fileInput = file.readlines()
        for w in fileInput:
            self.__words.append(w.strip('\n'))

        fileNameParts = iFile.split('_')
        self.__assignmentNum = fileNameParts[0][2:]

        file.close()

    def __createJSON(self):
        self.__jsonFile = open(f"{self.__assignmentNum}_found.json",'w')

    def __runAnalysis(self):
        dirName = f"/PRISM/data/assignments/assignment_{self.__assignmentNum}/bulk_submission"

        for f in os.listdir(dirName):
            if(not f.endswith(".csv")):
                self.__jsonFile.write('{\n\t"errors": [\n')
                self.__checkStudentFiles(f"{dirName}/{f}")
                self.__jsonFile.write('\t]\n')
                self.__jsonFile.write('}\n')
                break

    def __checkStudentFiles(self,section):
        for f in os.listdir(section):
            headerList = None
            if(not f.endswith(".json")):
                program = cindex.Index.create()
                # Parse program with all headers first
                ast = program.parse(f"{section}/{f}/main.cpp",args=['-std=c++11'])
                headerList = ast.get_includes()
                for i in headerList:
                    print(f"Header file: {i.include.name}")
                print(headerList)
                ast = program.parse(f"{section}/{f}/main.cpp",args=['-std=c++11','-nostdinc','-nostdlibinc'])

                # Start from the root cursor
                self.__checkAST(ast.cursor)
                break

    def __checkAST(self, currNode):
        for w in self.__words:
            if w == currNode.spelling:
              if currNode.kind != CursorKind.VAR_DECL or currNode.kind != CursorKind.DECL_REF_EXPR:
                print(f"{currNode.spelling} was found at {currNode.location.line}")

        for c in currNode.get_children():
            self.__checkAST(c)

def main(fileName):
    analyzer = KeywordAnalyzer(fileName)

if __name__ == "__main__":
    main(sys.argv[1])
