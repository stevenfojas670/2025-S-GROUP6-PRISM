
import json
import os
import sys

from asm_keyword_detection.AsmAnalyzer import AsmAnalyzer

class KeywordAnalyzer:

    __words:set = None
    __course:str = None
    __assignment:str = None
    __jsonFile = None
    __sections = None

    def __init__(self):
        self.__sections = dict(dict())
        self.__openAndValidateFile()
        self.__createOutputFile()
        self.__runAnalysis()

    '''
        This method is responsible for opening the input file
        containing the banned keywords, storing them into the
        KeywordAnalyzer's words array, and also getting the
        assignment for which the keyword analysis will be done for
    '''
    def __openAndValidateFile(self):
        # ERROR CHECK #1: Make sure the front end passed in the appropriate
        #                 file arguments to this script
        if len(sys.argv) != 2:
            print("Usage: python3 KeywordAnalyzer.py <fileName>.txt")
            exit(1)
        elif not sys.argv[1].endswith(".txt"):
            print("Error! A .txt file was not passed as an argument")
            exit(1)

        # ERROR CHECK #2: Make sure the file exists in the
        #                 keyword_detection package
        if not os.path.exists(sys.argv[1]):
            print("Error! Banned keyword file does not exist!")
            exit(1)

        fileParts = sys.argv[1].split("_")
        self.__course = fileParts[0][2:]
        self.__assignment = fileParts[1][2:]

        with open(sys.argv[1], 'r') as iFile:
            self.__words = set()
            for l in iFile.readlines():
                self.__words.add(l.strip('\n'))

    def __createOutputFile(self):
        self.__jsonFile = open(f"{self.__course}_{self.__assignment}_Found_Words.json", "w")

    def __runAnalysis(self):
        submissionDir = f"assignments/assignment_{self.__assignment}/bulk_submission"
        fileCount = len(os.listdir(submissionDir)) // 2
        for f in os.listdir(submissionDir):
            if not f.endswith(".csv"):
                section = f

                if self.__course == "135":
                    pass
                elif self.__course == "218":
                    asm = AsmAnalyzer(self.__words,self.__jsonFile,f"{submissionDir}/{section}",self.__assignment)
                    students = asm.tokenizeAssembly()
                    self.__sections[section] = students

                fileCount -= 1
                if fileCount > 0:
                    self.__jsonFile.write(',\n')
                else:
                    self.__jsonFile.write('\n')
                    break

        json.dump(self.__sections, self.__jsonFile,indent=4)


def main():
    KeywordAnalyzer()

if __name__ == "__main__":
    main()
