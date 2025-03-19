'''
    Created by Daniel Levy, 2/21/2025

    This script is a part of the Data Ingestion phase of PRISM.
'''
# Django setup
import os, django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE","prism_backend.settings")
# django.setup()

from zipfile import ZipFile
import pandas as pd
import json
from errors.DataIngestionError import DataIngestionError
import errors.DataIngestionErrorBuilder as eb

class CodeGradeDataIngestion:

    # Fields
    __dirName = None            # Directory containing all data (should be 'codegrade_data')
    __submissionFileName = None # Current course/assignment we are checking data for
    __className = None
    __section = None
    __semester = None
    __assignmentName = None
    __zipFileDirectory = None   # Directory that contains unzipped student submissions
    __submissions = None
    __users = None
    __metaData = None
    __errors = None

    fileSeen = set()    # Static set that keeps track of every file seen
    allErrors = list()  # Static list that keeps track of all errors found

    # Methods
    def __init__(self, dirName):
        self.__dirName = dirName
        self.__submissionFileName = ""
        self.__className = ""
        self.__section = ""
        self.__semester = ""
        self.__assignmentName = ""
        self.__zipFileDirectory = ""
        self.__submissions = list()
        self.__users = list()
        self.__metaData = list()
        self.__errors = list()

    '''
        This method will check the current directory and find the next ZIP
        file to extract and check the student submissions for.
    '''
    def __extractStudentFilesFromZIP(self):
        for file in os.listdir(self.__dirName):
            if file.endswith('.zip') and file not in self.fileSeen:
                self.__parseZipFileName(file)
                self.__zipFileDirectory = f"{self.__dirName}/{self.__submissionFileName}"

                zipFile = ZipFile(f"{self.__dirName}/{file}")
                zipFile.extractall(self.__zipFileDirectory)

                # Make sure the ZIP file actually contains data.
                if os.listdir(self.__zipFileDirectory) == []:
                    self.__errors.append(eb.DataIngestionErrorBuilder()
                                         .addFileName(self.__zipFileDirectory)
                                         .addMsg(f"There is no student submission files found in {self.__zipFileDirectory}")
                                         .createError())
                    raise ValueError()

                self.fileSeen.add(file)
                return

        # If we reach this point, then we have either have a duplicated ZIP file in the directory
        # or there are no ZIP files in the directory, so we have to create an error
        self.__errors.append(eb.DataIngestionErrorBuilder()
                             .addFileName(self.__dirName)
                             .addMsg(f"No .zip files were found containing student submission in {self.__dirName}")
                             .createError())
        raise ValueError()

    '''
        CodeGrade exports a ZIP file with the following title format:
            '<CS Class> <Section> - <Semester> <Assignment Name>'
        
        This method will simply parse the title and save each part to 
        the object's appropriate fields. No error handling is needed.
    '''
    def __parseZipFileName(self, name):
        self.__submissionFileName = name.removesuffix('.zip')
        zipFields = name.split('-', 2)

        canvasName = zipFields[0].split(' ')
        self.__className = canvasName[0] + ' ' + canvasName[1]
        self.__section = canvasName[2]

        self.__semester = zipFields[1].strip()
        self.__assignmentName = zipFields[2][:-4].strip()

    '''
        Every exported CodeGrade ZIP file will contain a .cg-info.json file that keeps
        track of all submissions and users. This is needed to ensure data authentication,
        so it must be present in the file.
    '''
    def __checkIfJSONFileExists(self):
        if not os.path.exists(f"{self.__zipFileDirectory}/.cg-info.json"):
            print("Error! The extracted zip file is missing the '.cg-info.json' file.")
            exit(1)

    '''
        Once the ZIP file has been extracted, we can now take the json 
        data and populate the submissions/users fields.
    '''
    def __extractJSON(self):
        self.__checkIfJSONFileExists()

        cgInfo = open(f'{self.__zipFileDirectory}/.cg-info.json', 'r')
        jsonStudentData = json.load(cgInfo)

        self.__submissions, self.__users = jsonStudentData['submission_ids'], jsonStudentData['user_ids']

    '''
        This method handles the extraction of CodeGrade metadata for
        each student which is exported through a CSV file.
    '''
    def __extractMetaDataFromCSV(self):
        for file in os.listdir(self.__dirName):
            if file == f"{self.__submissionFileName}.csv":
                csvFile = open(f"{self.__dirName}/{file}", 'r')
                df = pd.read_csv(csvFile)
                csvFile.close()
                self.__metaData = df
                return

        # ERROR CHECK #1: If we could not find the appropriate metadata .csv file
        #                 for the current ZIP file we extracted, generate an error
        self.__errors.append(eb.DataIngestionErrorBuilder()
                                     .addFileName(self.__submissionFileName)
                                     .addMsg(f"{self.__submissionFileName}.csv was not found in {self.__dirName}.")
                                     .createError())
        raise ValueError()

    '''
        Here, we verify that every submission ID is linked back to a student. We check
        the ZIP directory to make sure the submission is there and ensure the student 
        name matches the name associated with the given submission.
    '''
    def __verifyStudentSubmissionExists(self):
        for key, value in self.__submissions.items():
            try:
                subID, studentName = self.__checkIfStudentFileExists(key)
            except:
                continue
            else:

                if subID != value:
                    self.__errors.append(eb.DataIngestionErrorBuilder()
                                         .addFileName(self.__zipFileDirectory)
                                         .addMsg(f"The submission ID #{subID} for {studentName} is not correct.")
                                         .createError())

    '''
        Similarly, we check to make sure that each user ID in the metadata
        corresponds to exactly one submission, and that submission matches
        the appropriate student name.
    '''
    def __verifyStudentUserExistsInMetaData(self):
        for key, value in self.__users.items():

            try:
                subID, studentName = self.__checkIfStudentFileExists(key)
            except:
                continue
            else:

                entry = self.__metaData.loc[self.__metaData['Id'] == value]
                entriesFound = len(entry)

                if entriesFound < 1:
                    self.__errors.append(eb.DataIngestionErrorBuilder()
                                         .addFileName(self.__submissionFileName)
                                         .addMsg(f"User ID {value} does not have any metadata associated with it.")
                                         .createError())
                elif entriesFound > 1:
                    self.__errors.append(eb.DataIngestionErrorBuilder()
                                         .addFileName(self.__submissionFileName)
                                         .addMsg(f"User ID {value} has multiple metadata entries associated with it.")
                                         .createError())

                if entry.iloc[0, 2] != studentName:
                    self.__errors.append(eb.DataIngestionErrorBuilder()
                                         .addFileName(self.__submissionFileName)
                                         .addMsg(f"User ID {value} does not match the given name in the metadata file.")
                                         .createError())

    def __checkIfStudentFileExists(self, fileName):
        subID, studentName = fileName.split('-', 1)
        studentName = studentName.strip()

        subID = int(subID.strip())

        if fileName not in os.listdir(self.__zipFileDirectory):
            self.__errors.append(eb.DataIngestionErrorBuilder()
                                 .addFileName(self.__submissionFileName)
                                 .addMsg(f"Submission for {studentName} is missing in zip directory.")
                                 .createError())
            raise ValueError()

        return subID, studentName

    def extractData(self):
        submissionDirLength = len(os.listdir("codegrade_data"))

        for i in range(submissionDirLength//2):
            try:
                self.__extractStudentFilesFromZIP()
                self.__extractJSON()
                self.__extractMetaDataFromCSV()
                self.__verifyStudentSubmissionExists()
                self.__verifyStudentUserExistsInMetaData()
            except:
                for e in self.__errors:
                    self.allErrors.append(e)
                self.__errors = list()
                continue
            else:
                pass

        if(len(self.allErrors) > 0):
            DataIngestionError.createErrorJSON("codegrade_data_errors",self.allErrors)

def main():
    cgData = CodeGradeDataIngestion("codegrade_data")
    cgData.extractData()

if __name__ == "__main__":
    main()
