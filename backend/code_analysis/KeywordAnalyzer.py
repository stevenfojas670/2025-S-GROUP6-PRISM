
import sys
import os

class KeywordAnalyzer:

    __words:set = None
    __course:str = None
    __assignment:str = None

    def __init__(self):
        self.__openAndValidateFile()
        print(self.__course,self.__assignment,self.__words)

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

def main():
    KeywordAnalyzer()

if __name__ == "__main__":
    main()
