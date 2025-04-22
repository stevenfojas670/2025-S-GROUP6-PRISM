
import os

class AssemblyAnalyzer:
    __assignmentNum = None
    __bannedInstrs = None

    def __init__(self,file):
        self.__bannedInstrs = set()
        self.__validateInputFile(file)

    def __validateInputFile(self, iFile):
        # ERROR CHECK #1: Make sure the file exists in the same directory
        #                 as the script for ease of use
        if not os.path.exists(iFile):
            exit(1)

        if not iFile.find("_"):
            print("Error! Input file is invalid, the title must be as<asstNum>_bannedWords.txt")
            exit(1)

        with open(iFile,'r') as f:
            for line in f.readlines():
                self.__bannedInstrs.add(line.strip("\n"))

            self.__assignmentNum = iFile.split("_")[0][2:]

def main():
    AssemblyAnalyzer("as1_bannedWords.txt")

if __name__ == "__main__":
    main()