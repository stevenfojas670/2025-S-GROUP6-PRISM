'''
    Created by Daniel Levy, 3/17/2025

    This script is designed to take and validate all Canvas
    gradebook data and then update the database.
'''

import os
import pandas as pd
import json
import errors.DataIngestionErrorBuilder as eb

class CanvasDataIngestion:

    # Class Fields
    __dirName = None    # Directory where Canvas data is located
    __fileName = None   # Current file we are checking
    __data = None       # Dataframe to store file contents
    __course = None
    __section = None
    __year = None
    __semester = None   # Spring, Summer, or Fall
    __metaID = None     # List of Canvas metadata info
    __errors = None     # List of errors

    def __init__(self,dirName):
        self.__dirName = dirName
        self.__fileName = ""
        self.__data = ""
        self.__course = ""
        self.__section = ""
        self.__year = ""
        self.__semester = ""
        self.__metaID = list()
        self.__errors = list()

    def __parseCanvasFileName(self,file):
        fields = file.split('-')

        courseInfo = fields[3].split('_')
        self.__course = courseInfo[0] + courseInfo[1]
        self.__section = courseInfo[2]

        semesterInfo = fields[4].split('_')
        self.__year = semesterInfo[1]
        self.__semester = semesterInfo[2].removesuffix('.csv')
        self.__fileName = file

    def __convertToDataFrame(self):
        csvFile = open(f"{self.__dirName}/{self.__fileName}",'r')
        self.__data = pd.read_csv(csvFile)
        csvFile.close()

    def __validateData(self):
        self.__metaID = self.__data['Section'].iloc[0]
        for index, student in self.__data.iterrows():
            if student['SIS User ID'] != student['SIS Login ID']:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index+1)
                                     .addMsg(f"The User ID for f{student['Student']} does not "
                                             f"match the Login ID")
                                     .createError())

            if student['Section'] != self.__metaID:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index+1)
                                     .addMsg(f"The Canvas metadata ID does not match for f{student['Student']}.")
                                     .createError())

            self.courseInfo = self.__getCourseMetaData(student['Section'])

            if self.courseInfo[0] != self.__semester:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The semester for f{student['Student']} does not "
                                             f"match the Canvas semester.")
                                     .createError())
            if self.courseInfo[1] != self.__course:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The course name for f{student['Student']} does not "
                                             f"match the Canvas course name.")
                                     .createError())
            if self.courseInfo[2] != self.__section:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The section number for f{student['Student']} does not "
                                             f"match the Canvas section.")
                                     .createError())

    def __getCourseMetaData(self, metaID):
        courseInfo = metaID.split('-')
        metaData = list()

        if courseInfo[0][-1] == "2":
            metaData.append("Sprg")
        elif courseInfo[0][-1] == "5":
            metaData.append("Sumr")
        elif courseInfo[0][-1] == "8":
            metaData.append("Fall")
        else:
            print("Error!")

        metaData.append(courseInfo[1]+courseInfo[2])
        metaData.append(courseInfo[3][3:])
        metaData.append(courseInfo[4])

        return metaData

    def __createErrorJSON(self):
        errorCount = len(self.__errors)
        with open("canvasDataIngestionErrors.json",'w') as oFile:
            oFile.write('{\n\t"errors": [\n')
            for i,e in enumerate(self.__errors):
                json.dump(e.__dict__,oFile,indent=4)
                if(i != errorCount-1):
                    oFile.write(',\n')
            oFile.write('\t]\n')
            oFile.write('}\n')

    def extractData(self):
        for file in os.listdir(self.__dirName):
            if not file.endswith('.csv'):
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(file)
                                     .addMsg(f"The file '{file}' is not a valid .csv file.")
                                     .createError())
                continue

            self.__parseCanvasFileName(file)
            self.__convertToDataFrame()
            self.__validateData()

        if len(self.__errors) > 0:
            self.__createErrorJSON()

def main():
    ingest = CanvasDataIngestion('canvas_data')
    ingest.extractData()

if __name__ == "__main__":
    main()
