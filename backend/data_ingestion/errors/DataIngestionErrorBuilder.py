'''
    Created by Daniel Levy, 3/17/2025

    This is a simple error builder class that can be used for PRISM's
    data ingestion. Every builder will create a new error, and we can
    add the error information we need based on what we're checking.
'''
import errors.DataIngestionErrorFactory as ef

class DataIngestionErrorBuilder:

    __error = None  # Copy of Error object

    def __init__(self):
        self.__error = ef.DataIngestionErrorFactory().createError()

    def createError(self):
        return self.__error

    def addFileName(self,fileName):
        self.__error.setFileName(fileName)
        return self

    def addLine(self,line):
        self.__error.setLine(line)
        return self

    def addMsg(self,msg):
        self.__error.setMsg(msg)
        return self
