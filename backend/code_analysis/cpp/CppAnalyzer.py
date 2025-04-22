"""
Created by Daniel Levy, 4/19/2025.

This script is designed to analyze blacklisted keywords from
student submissions. A user on the front end will manually
input which keywords and/or libraries that students should not
be using in their code. The file will then be sent to this script
for processing all student submissions, and we will return an
error json back to the front end to display the results to the user.
"""
import sys
import os
import json

from clang import cindex
from clang.cindex import CursorKind


class CppAnalyzer:
    """Create object to perform keyword analysis."""

    __words = None
    __subDir = None
    __assignment = None
    __students:dict = None

    # Methods
    def __init__(self, words, subDir, assignment):
        """Construct CppAnalyzer object."""
        self.__words = words
        self.__subDir = subDir
        self.__assignment = assignment


    '''
        This is a helper method for runAnalysis. The goal is to parse each
        student's input file and manually verify whether or not they used
        blacklisted keywords and/or headers. All information will be written
        into the JSON file.
    '''
    def generateAST(self):
        for f in os.listdir(self.__subDir):
            studentName = f.split('-')[1].strip()
            with open(f"{self.__subDir}/{f}/as{self.__assignment}.asm",'r') as submission:
                if not f.endswith(".json"):
                    headers = self.__checkHeaders(f"{self.__subDir}/{f}/main.cpp")



        #
        #
        #         program = cindex.Index.create()
        #
        #         ast = program.parse(f"{section}/{f}/main.cpp", args=['-std=c++11', '-nostdinc', '-nostdlibinc'])
        #
        #         self.__checkAST(ast.cursor)
        #
        #         if len(self.__found) > 0:
        #             if (filesAdded > 0):
        #                 self.__jsonFile.write(',\n')
        #             filesAdded += 1
        #
        #             self.__jsonFile.write('\n\t\t' + f'"{f.split("-")[1].strip("_")}"' + ': \n')
        #
        #             json.dump(self.__found, self.__jsonFile, indent=8)
        #             self.__found.clear()
        #             if fileCount == filesAdded:
        #                 break
        #         headers.clear()
        #         for i in range(len(self.__wordsCount)):
        #             self.__wordsCount[i] = 0


    '''
        This method is designed to check all import statements at the start
        of a student's file and manually verify whether or not a library
        specified by the user was found inside a student's file. All we are
        going to do is add the library name so it can be saved in the JSON file
    '''
    def __checkHeaders(self, file):
        foundHeaders = list()
        with open(file, 'r') as iFile:
            includeFound = False
            for line in iFile:
                if line.startswith("#include"):
                    includeFound = True
                    headerName = ""
                    if line.find("<"):
                        headerName = line[line.find("<") + 1:line.find(">")]
                    else:
                        headerName = line[line.find(" ") + 1:line.find(" ")]

                    for w in self.__words:
                        if w == headerName:
                            foundHeaders.append(w)
                elif includeFound: return foundHeaders

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
        for i,w in enumerate(self.__words):
            if w == currNode.spelling:
                if currNode.kind != CursorKind.VAR_DECL or currNode.kind != CursorKind.DECL_REF_EXPR:
                    self.__found.append({'word': w, 'line': currNode.location.line})
                    self.__wordsCount[i] += 1

        for c in currNode.get_children():
            self.__checkAST(c)


def main(fileName):
    """Interfaces with keywordAnalysis class."""
    CppAnalyzer(fileName)


if __name__ == "__main__":
    main(sys.argv[1])
