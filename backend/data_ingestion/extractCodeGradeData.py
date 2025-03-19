'''
    Created by Daniel Levy, 2/21/2025

    This script is a part of the Data Ingestion phase of PRISM.
'''
from zipfile import ZipFile
import pandas as pd
import json
# Django setup
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","prism_backend.settings")
django.setup()

class CodeGradeData:



    fileSeen = set()    # Hash set that keeps track of every file

    '''
        Constructor will initialize this class when we are extracting
        student data from CodeGrade
    '''
    def __init__(self, dirName):
        self.__dirName = dirName
        self.__submissionFileName = ""
        self.__className = self.__section = self.semester = self.assignmentName = self.zipFileDirectory = ""
        self.__submissions = self.users = self.metaData = self.errors = []
        self.extractStudentFilesFromZIP()

    def extractStudentFilesFromZIP(self):
        for file in os.listdir(self.__dirName):
            if file.endswith('.zip') and file not in fileSeen:
                self.parseZipFileName(file)
                self.zipFileDirectory = f"{self.__dirName}/{self.__submissionFileName}"

                zipFile = ZipFile(f"{self.__dirName}/{file}")
                zipFile.extractall(self.zipFileDirectory)

                # Make sure the ZIP file actually contains data.
                if os.listdir(self.zipFileDirectory) == []:
                    print(
                        f"Error! The zip file for Assignment {self.assignmentName} did not contain any student submissions!")
                    exit(1)

                fileSeen.add(file)
                return

        # If we reach this point, then no valid ZIP file was found. Once we integrate
        # the CodeGrade API with this script, we don't need this error check anymore.
        print("Error! No .zip file containing student submissions was found.")
        exit(1)

    '''
        CodeGrade exports a ZIP file with the following title format:
            '<CS Class> <Section> - <Semester> <Assignment Name>'
        
        This method will simply parse the title and save each part to 
        the object's appropriate fields. No error handling is needed.
    '''
    def parseZipFileName(self, name):
        self.__submissionFileName = name.removesuffix('.zip')
        zipFields = name.split('-', 2)

        canvasName = zipFields[0].split(' ')
        self.__className = canvasName[0] + ' ' + canvasName[1]
        self.__section = canvasName[2]

        self.semester = zipFields[1].strip()
        self.assignmentName = zipFields[2][:-4].strip()

    '''
        Every exported CodeGrade ZIP file will contain a .cg-info.json file that keeps
        track of all submissions and users. This is needed to ensure data authentication,
        so it must be present in the file.
    '''
    def checkIfJSONFileExists(self):
        if not os.path.exists(f"{self.zipFileDirectory}/.cg-info.json"):
            print("Error! The extracted zip file is missing the '.cg-info.json' file.")
            exit(1)

    '''
        Once the ZIP file has been extracted, we can now take the json 
        data and populate the submissions/users fields.
    '''
    def extractJSON(self):
        self.checkIfJSONFileExists()

        cgInfo = open(f'{self.zipFileDirectory}/.cg-info.json', 'r')
        jsonStudentData = json.load(cgInfo)

        self.__submissions, self.users = jsonStudentData['submission_ids'], jsonStudentData['user_ids']

    '''
        This method handles the extraction of CodeGrade metadata for
        each student which is exported through a CSV file.
    '''
    def extractMetaDataFromCSV(self):
        for file in os.listdir(self.__dirName):
            if file == f"{self.__submissionFileName}.csv":
                csvFile = open(f"{self.__dirName}/{file}", 'r')
                df = pd.read_csv(csvFile)
                csvFile.close()
                self.metaData = df
                return

        print("No .csv file containing student metadata was found.")
        exit(1)

    '''
        Here, we verify that every submission ID is linked back to a student. We check
        the ZIP directory to make sure the submission is there and ensure the student 
        name matches the name associated with the given submission.
    '''
    def verifyStudentSubmissionExists(self):
        for key, value in self.__submissions.items():
            subID, studentName = self.checkIfStudentFileExists(key)

            if subID != value:
                self.addError(f"Submission ID #{subID} does not match for {studentName}.")

    '''
        Similarly, we check to make sure that each user ID in the metadata
        corresponds to exactly one submission, and that submission matches
        the appropriate student name.
    '''
    def verifyStudentUserExistsInMetaData(self):
        for key, value in self.users.items():

            subID, studentName = self.checkIfStudentFileExists(key)

            entry = self.metaData.loc[self.metaData['Id'] == value]
            entriesFound = len(entry)

            if entriesFound < 1:
                self.addError(f"Error! No metadata for user ID {value} was found.", 'meta')

            if entriesFound > 1:
                self.addError(f"Error! User ID {value} has more than one entry.", 'meta')

            if entry.iloc[0, 2] != studentName:
                self.addError(f"Error! User ID {value} does not have a matching name.", 'meta')

    def checkIfStudentFileExists(self, fileName):
        subID, studentName = fileName.split('-', 1)
        studentName = studentName.strip()

        subID = int(subID.strip())

        if fileName not in os.listdir(self.zipFileDirectory):
            self.addError(f"Submission for {studentName} is missing.",fileName)

        return subID, studentName

    def addError(self, msg, file):
        self.errors.append(
            {
                'message': msg,
                'file': file
            }
        )

    def printDebugInfo(self):
        print(self.__submissions)
        print(self.users)
        print(self.metaData)

def main():
    submissionDirLength = len(os.listdir("codegrade_data"))

    for i in range(submissionDirLength//2):
        cgData = CodeGradeData("codegrade_data")

        cgData.extractJSON()
        cgData.extractMetaDataFromCSV()
        cgData.verifyStudentSubmissionExists()
        cgData.verifyStudentUserExistsInMetaData()

        if (len(cgData.errors) > 0):
            print("An error occurred parsing the data.")

        cgData.printDebugInfo()

if __name__ == "__main__":
    main()
