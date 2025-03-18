'''
Created by Daniel Levy, 3/17/2025

This script is designed to take Canvas data to create
initial course/student submission in the database.
'''

import os
import pandas as pd
import json


class CanvasDataIngestion:
    def __init__(self,dirName):
        self.dirName = dirName
        self.data = ""
        self.course = ""
        self.section = ""
        self.year = ""
        self.semester = ""
        self.metaID = list()

    def convertToDataFrame(self,file):
        if not file.endswith('.csv'):
            print('Error!')

        csvFile = open(f"{self.dirName}/{file}",'r')
        self.data = pd.read_csv(csvFile)
        csvFile.close()

    def parseCanvasFileName(self,file):
        fields = file.split('-')

        courseInfo = fields[3].split('_')
        self.course = courseInfo[0] + courseInfo[1]
        self.section = courseInfo[2]

        semesterInfo = fields[4].split('_')
        self.year = semesterInfo[1]
        self.semester = semesterInfo[2].removesuffix('.csv')

    def validateData(self):
        self.metaID = self.data['Section'].iloc[0]
        for index, student in self.data.iterrows():
            if student['SIS User ID'] != student['SIS Login ID']:
                print("Error!")

            if student['Section'] != self.metaID:
                print("Error!")

            self.courseInfo = self.getCourseMetaData(student['Section'])

            if self.courseInfo[0] != self.semester:
                print("ERROR!")
            if self.courseInfo[1] != self.course:
                print("Error!")
            if self.courseInfo[2] != self.section:
                print("Error!")

    def getCourseMetaData(self, metaID):
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

    def extractData(self):
        for file in os.listdir(self.dirName):
            if not file.endswith('.csv'):
                print("Error!")

            self.parseCanvasFileName(file)
            self.convertToDataFrame(file)
            self.validateData()

def main():
    ingest = CanvasDataIngestion('canvas_data')
    ingest.extractData()

if __name__ == "__main__":
    main()
