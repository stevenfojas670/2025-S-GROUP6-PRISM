import sys
import os

class KeywordAnalyzer:
    __assignmentNum = None
    __words = None

    def __init__(self, inputFile):
        self.__words = list()
        self.openAndValidateFile(inputFile)

    '''
        This method is responsible for opening the input file
        containing the banned keywords, storing them into the
        KeywordAnalyzer's words array, and also getting the 
        assignment for which the keyword analysis will be done for
    '''
    def openAndValidateFile(self,iFile):
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
        __assignmentNum = fileNameParts[0][2:]

        file.close()

def main(fileName):
    analyzer = KeywordAnalyzer(fileName)

if __name__ == "__main__":
    main(sys.argv[1])
