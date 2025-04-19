import sys
import os
import json

from clang import cindex
from clang.cindex import CursorKind

class KeywordAnalyzer:
    __assignmentNum = None
    __words = None
    __jsonFileName = None
    __jsonFile = None
    __found = None

    def __init__(self, inputFile):
        self.__words = list()
        self.__found = list(dict())
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
        self.__jsonFileName = f"{self.__assignmentNum}_found.json"
        self.__jsonFile = open(self.__jsonFileName,'w')

    def __runAnalysis(self):
        dirName = f"/PRISM/data/assignments/assignment_{self.__assignmentNum}/bulk_submission"
        self.__jsonFile.write('{\n\t')

        for f in os.listdir(dirName):
            if(not f.endswith(".csv")):
                section = f.split("_")[2]
                self.__jsonFile.write(f'"{section}"' + ': [\n')
                self.__checkStudentFiles(f"{dirName}/{f}")
                self.__jsonFile.write(',\n')

        self.__jsonFile.write('}\n')

    def __checkStudentFiles(self,section):
        for f in os.listdir(section):
            headers = list()

            if(not f.endswith(".json")):
                self.__checkHeaders(f"{section}/{f}/main.cpp",headers)
                if (len(headers) > 0):
                    self.__jsonFile.write('{\n\t\t' + f'"{f.split("-")[1].strip("_")}"' + ':\n')
                    json.dump({"headers": headers}, self.__jsonFile, indent=8)

                program = cindex.Index.create()

                ast = program.parse(f"{section}/{f}/main.cpp",args=['-std=c++11','-nostdinc','-nostdlibinc'])

                self.__checkAST(ast.cursor)
                print(self.__found)
                if(len(self.__found) > 0):
                    if(len(headers) == 0):
                        self.__jsonFile.write('{\n\t\t' + f'"{f.split("-")[1].strip("_")}"' + ':\n')

                    json.dump(self.__found,self.__jsonFile,indent=8)
                    self.__found.clear()

                headers.clear()

    def __checkHeaders(self,file,headers):
        with open(file,'r') as iFile:
            for line in iFile:
                if not line.startswith("#include"):
                    break

                lib = line[line.find("<")+1:line.find(">")]
                for w in self.__words:
                    if w == lib:
                        headers.append(w)

    def __checkAST(self, currNode):
        for w in self.__words:
            if w == currNode.spelling:
              if currNode.kind != CursorKind.VAR_DECL or currNode.kind != CursorKind.DECL_REF_EXPR:
                    self.__found.append({'word' : w, 'line' : currNode.location.line})

        for c in currNode.get_children():
            self.__checkAST(c)

def main(fileName):
    analyzer = KeywordAnalyzer(fileName)

if __name__ == "__main__":
    main(sys.argv[1])
