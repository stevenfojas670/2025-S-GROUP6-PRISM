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

    '''
        This method will parse the file name and extract 
        the info related to the Canvas course, so we may
        validate each student's Canvas meta ID.
    '''
    def __parseCanvasFileName(self,file):
        fields = file.split('-')

        courseInfo = fields[3].split('_')
        self.__course = courseInfo[0] + courseInfo[1]
        self.__section = courseInfo[2]

        semesterInfo = fields[4].split('_')
        self.__year = semesterInfo[1]
        self.__semester = semesterInfo[2].removesuffix('.csv')
        self.__fileName = file

    '''
        Here, we are going to take our .csv file and extract the info
        into a Pandas dataframe so we can use it
    '''
    def __convertToDataFrame(self):
        csvFile = open(f"{self.__dirName}/{self.__fileName}",'r')
        self.__data = pd.read_csv(csvFile)
        csvFile.close()

    '''
        This will be our main error handling method that will check 
        if all the individual student entries in the .csv file match
        the expected data for the Canvas course.
    '''
    def __validateData(self):
        self.__metaID = self.__data['Section'].iloc[0]
        for index, student in self.__data.iterrows():
            # Error Check #1: Make sure the student's User/login ID
            #                 match (it should be their ACE ID)
            if student['SIS User ID'] != student['SIS Login ID']:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index+1)
                                     .addMsg(f"The User ID for f{student['Student']} does not "
                                             f"match the Login ID")
                                     .createError())

            # Error Check #2: Make sure the Canvas meta ID matches the
            #                 meta ID for the first student in the file
            if student['Section'] != self.__metaID:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index+1)
                                     .addMsg(f"The Canvas metadata ID does not match for f{student['Student']}.")
                                     .createError())

            self.courseInfo = self.__getCourseMetaData(student['Section'])

            # Error Check #3: Make sure the semester matches the semester
            #                 given in the file name
            if self.courseInfo[0] != self.__semester:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The semester for f{student['Student']} does not "
                                             f"match the Canvas semester.")
                                     .createError())

            # Error Check #4: Make sure the course matches the course
            #                 given in the file name
            if self.courseInfo[1] != self.__course:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The course name for f{student['Student']} does not "
                                             f"match the Canvas course name.")
                                     .createError())

            # Error Check #5: Make sure the section matches the section
            #                 given in the file name
            if self.courseInfo[2] != self.__section:
                self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__fileName)
                                     .addLine(index + 1)
                                     .addMsg(f"The section number for f{student['Student']} does not "
                                             f"match the Canvas section.")
                                     .createError())

    '''
        When we are trying to validate the student data, we must parse
        the Canvas meta ID per student to make sure each part of the ID
        matches the provided information in the title of the .csv file
    '''
    def __getCourseMetaData(self, metaID):
        courseInfo = metaID.split('-')
        metaData = list()

        # The semester will be denoted by the last number in
        # the first field of the Canvas meta ID
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

    '''
        If we encounter any errors, then this method will create a JSON
        file containing all the errors that can then be parsed/displayed
        to the user however we want.
    '''
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

    '''
        This will be the main method that a user will call to extract
        all information from the exported Canvas gradebook file.
    '''
    def extractData(self):
        for file in os.listdir(self.__dirName):
            # Error Check #1: Make sure each file in the canvas_data
            #                 directory is indeed a .csv file
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
