
class KeywordAnalyzer:
    __inputFile = None

    def __init__(self, inputFile):
        self.openAndValidateFile(inputFile)

    def openAndValidateFile(self,iFile):
        try:
            file = open(iFile,'r')
        except:
            print("ERROR!")
            exit(1)
        else:
            __inputFile = file.readlines()

def main():
    analyzer = KeywordAnalyzer('banned_words.txt')

if __name__ == "__main__":
    main()
