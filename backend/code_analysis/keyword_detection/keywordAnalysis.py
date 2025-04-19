'''
    Created by Daniel Levy, 4/19/2025

    This script is designed to analyze blacklisted keywords from
    student submissions. A user on the front end will manually
    input which keywords and/or libraries that students should not
    be using in their code. The file will then be sent to this script
    for processing all student submissions, and we will return an
    error json back to the front end to display the results to the user.
'''
import sys
import os
import json

from clang import cindex
from clang.cindex import CursorKind

class KeywordAnalyzer:
    # Fields
    __assignmentNum = None
    __words = None
    __jsonFileName = None
    __jsonFile = None
    __found = None

    # Methods
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

    '''
        This method is responsible for opening and creating the JSON
        output file that will be used by the front end
    '''
    def __createJSON(self):
        self.__jsonFileName = f"{self.__assignmentNum}_found.json"
        self.__jsonFile = open(self.__jsonFileName,'w')

    '''
        This is the main method for KeywordAnalyzer. We will do a bulk analysis
        for every section by looking at student file located in each directory.
        Once this has been completed, we can then access a JSON file that will 
        contain all the students who violated the rules for the assignment
    '''
    def __runAnalysis(self):
        dirName = f"/PRISM/data/assignments/assignment_{self.__assignmentNum}/bulk_submission"
        self.__jsonFile.write('{\n\t')

        fileCount = len(os.listdir(dirName))//2
        for f in os.listdir(dirName):
            if(not f.endswith(".csv")):
                section = f.split("_")[2]
                self.__jsonFile.write(f'"{section}"' + ': {\n')
                self.__checkStudentFiles(f"{dirName}/{f}")
                self.__jsonFile.write('}')
                fileCount -= 1
                if(fileCount > 0):
                    self.__jsonFile.write(',\n')
                else:
                    self.__jsonFile.write('\n')
                    break
        self.__jsonFile.write('}\n')

    '''
        This is a helper method for runAnalysis. The goal is to parse each
        student's input file and manually verify whether or not they used
        blacklisted keywords and/or headers. All information will be written
        into the JSON file.
    '''
    def __checkStudentFiles(self,section):
        fileCount = len(os.listdir(section))//2
        filesAdded = 0

        for f in os.listdir(section):
            headers = list()

            if(not f.endswith(".json")):
                self.__checkHeaders(f"{section}/{f}/main.cpp",headers)
                if (len(headers) > 0):
                    self.__found.append({"headers": headers})

                program = cindex.Index.create()

                ast = program.parse(f"{section}/{f}/main.cpp",args=['-std=c++11','-nostdinc','-nostdlibinc'])

                self.__checkAST(ast.cursor)

                if(len(self.__found) > 0):
                    if (filesAdded > 0):
                        self.__jsonFile.write(',\n')
                    filesAdded += 1

                    self.__jsonFile.write('\n\t\t' + f'"{f.split("-")[1].strip("_")}"' + ': \n')

                    json.dump(self.__found,self.__jsonFile,indent=8)
                    self.__found.clear()
                headers.clear()

    '''
        This method is designed to check all import statements at the start
        of a student's file and manually verify whether or not a library 
        specified by the user was found inside a student's file. All we are 
        going to do is add the library name so it can be saved in the JSON file
    '''
    def __checkHeaders(self,file,headers):
        with open(file,'r') as iFile:
            for line in iFile:
                if not line.startswith("#include"):
                    break

                lib = line[line.find("<")+1:line.find(">")]
                for w in self.__words:
                    if w == lib:
                        headers.append(w)

    '''
        This method will analyze the AST for a student's input file and
        check if there any usages of keywords they weren't suppose to use.
        In this case, we are checking if the words used are not identifiers, 
        so we manually verify if the current node represents a VARDECL or a 
        NAMEEXPR first prior to adding the result to our error array. For right 
        now, we note which word was used followed by the line number it came
        from.
    '''
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
