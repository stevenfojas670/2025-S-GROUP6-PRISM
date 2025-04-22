
import sys
import os

class KeywordAnalyzer:

    def __init__(self):
        self.__openAndValidateFile()
    '''
        This method is responsible for opening the input file
        containing the banned keywords, storing them into the
        KeywordAnalyzer's words array, and also getting the
        assignment for which the keyword analysis will be done for
    '''

    def __openAndValidateFile(self):
        # ERROR CHECK #1: Make sure the file exists in the
        #                 keyword_detection package
        if not os.path.exists(sys.argv[1]):
            print("Error! Banned keyword file does not exist!")
            exit(1)

        file = open(sys.argv[1], 'r')

        fileInput = file.readlines()
        for w in fileInput:
            self.__words.append(w.strip('\n'))
            self.__wordsCount.append(0)

        fileNameParts = sys.argv[1].split('_')
        self.__assignmentNum = fileNameParts[0][2:]

        file.close()


def main():
    KeywordAnalyzer()

if __name__ == "__main__":
    main()
