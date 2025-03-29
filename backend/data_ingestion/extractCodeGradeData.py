"""Created by Daniel Levy, 2/21/2025.

This script handles ingestion of CodeGrade metadata into the database.
It focuses on models from the `assignments` app and performs validation
of data extracted from CodeGrade-generated files.
"""

import os
import json
import math
import django
import pandas as pd
from zipfile import ZipFile

from assignments.models import Student, Assignment, Submission
import data_ingestion.errors.DataIngestionErrorBuilder as eb
from data_ingestion.errors.DataIngestionError import DataIngestionError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prism_backend.settings")
django.setup()


class CodeGradeDataIngestion:
    """Ingest and validate CodeGrade data, then populate the database."""

    __dirName = None
    __submissionFileName = None
    __className = None
    __section = None
    __semester = None
    __assignmentName = None
    __zipFileDirectory = None
    __submissions = None
    __users = None
    __metaData = None
    __errors = None

    fileSeen = set()
    allErrors = list()

    def __init__(self, dirName):
        """Initialize the class with directory path and reset state."""
        self.__dirName = dirName
        self.__submissionFileName = ""
        self.__className = ""
        self.__section = ""
        self.__semester = ""
        self.__assignmentName = ""
        self.__zipFileDirectory = ""
        self.__submissions = []
        self.__users = []
        self.__metaData = []
        self.__errors = []

    def __extractStudentFilesFromZIP(self):
        """Extract and unzip the next unseen CodeGrade submission ZIP."""
        for file in os.listdir(self.__dirName):
            if file.endswith(".zip") and file not in CodeGradeDataIngestion.fileSeen:
                self.__parseZipFileName(file)
                self.__zipFileDirectory = os.path.join(
                    self.__dirName, self.__submissionFileName
                )
                zipFile = ZipFile(os.path.join(self.__dirName, file))
                zipFile.extractall(self.__zipFileDirectory)
                CodeGradeDataIngestion.fileSeen.add(file)
                return

        self.__errors.append(
            eb.DataIngestionErrorBuilder()
            .addFileName(self.__dirName)
            .addMsg("A duplicate or missing .zip file was found in the directory.")
            .createError()
        )
        raise ValueError()

    def __parseZipFileName(self, name):
        """Parse ZIP file name to extract class, section, semester, and assignment."""
        self.__submissionFileName = name.removesuffix(".zip")
        zipFields = name.split("-", 2)
        canvasName = zipFields[0].split(" ")
        self.__className = f"{canvasName[0]} {canvasName[1]}"
        self.__section = canvasName[2]
        self.__semester = zipFields[1].strip()
        self.__assignmentName = zipFields[2][:-4].strip()

    def __checkIfJSONFileExists(self):
        """Ensure .cg-info.json file exists in the extracted ZIP folder."""
        json_path = os.path.join(self.__zipFileDirectory, ".cg-info.json")
        if not os.path.exists(json_path):
            self.__errors.append(
                eb.DataIngestionErrorBuilder()
                .addFileName(self.__dirName)
                .addMsg("The .cg-info.json file is missing.")
                .createError()
            )

    def __extractJSON(self):
        """Extract submission and user IDs from .cg-info.json."""
        self.__checkIfJSONFileExists()
        json_path = os.path.join(self.__zipFileDirectory, ".cg-info.json")
        with open(json_path, "r") as cgInfo:
            jsonStudentData = json.load(cgInfo)
        self.__submissions = jsonStudentData["submission_ids"]
        self.__users = jsonStudentData["user_ids"]

    def __extractMetaDataFromCSV(self):
        """Extract metadata CSV corresponding to the ZIP file."""
        for file in os.listdir(self.__dirName):
            if file == f"{self.__submissionFileName}.csv":
                csv_path = os.path.join(self.__dirName, file)
                with open(csv_path, "r") as csvFile:
                    self.__metaData = pd.read_csv(csvFile)
                return

        self.__errors.append(
            eb.DataIngestionErrorBuilder()
            .addFileName(self.__submissionFileName)
            .addMsg(f"{self.__submissionFileName}.csv not found in {self.__dirName}.")
            .createError()
        )
        raise ValueError()

    def __verifyStudentSubmissionExists(self):
        """Ensure each submission ID links to a valid student file."""
        for key, value in self.__submissions.items():
            try:
                sub_id, student_name = self.__checkIfStudentFileExists(key)
            except Exception:
                continue
            if sub_id != value:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__zipFileDirectory)
                    .addMsg(f"The submission ID #{sub_id} for {student_name} is incorrect.")
                    .createError()
                )

    def __verifyStudentUserExistsInMetaData(self):
        """Verify that each user ID matches metadata and student name."""
        for key, value in self.__users.items():
            try:
                sub_id, student_name = self.__checkIfStudentFileExists(key)
            except Exception:
                raise ValueError()

            entry = self.__metaData.loc[self.__metaData["Id"] == value]
            entries_found = len(entry)

            if entries_found < 1:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__submissionFileName)
                    .addMsg(f"User ID {value} has no metadata.")
                    .createError()
                )
                raise ValueError()

            if entries_found > 1:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__submissionFileName)
                    .addMsg(f"User ID {value} has multiple metadata entries.")
                    .createError()
                )
                raise ValueError()

            if entry.iloc[0, 2] != student_name:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__submissionFileName)
                    .addMsg(f"User ID {value} does not match the student name.")
                    .createError()
                )
                raise ValueError()

    def __checkIfStudentFileExists(self, file_name):
        """Check if the submission folder exists for a student.

        Args:
            file_name (str): Filename in the format 'submission_id - student_name'.

        Returns:
            tuple: (submission_id, student_name)

        Raises:
            ValueError: If the directory for the student's submission is missing.
        """
        sub_id, student_name = file_name.split("-", 1)
        sub_id = int(sub_id.strip())
        student_name = student_name.strip()

        if file_name not in os.listdir(self.__zipFileDirectory):
            self.__errors.append(
                eb.DataIngestionErrorBuilder()
                .addFileName(self.__submissionFileName)
                .addMsg(f"Submission for {student_name} is missing in the ZIP directory.")
                .createError()
            )
            raise ValueError()

        return sub_id, student_name

    def __populateDatabase(self):
        """Populate the database with student entries from metadata."""
        for _, student in self.__metaData.iterrows():
            names = student["Name"].split(" ")
            email = student["Username"] + "@unlv.nevada.edu"

            try:
                Student.objects.get_or_create(
                    email=email,
                    codeGrade_id=student["Id"],
                    username=student["Username"],
                    first_name=names[0],
                    last_name=names[1],
                )
            except Student.DoesNotExist:
                new_student = Student(
                    email=email,
                    codeGrade_id=student["Id"],
                    username=student["Username"],
                    first_name=names[0],
                    last_name=names[1],
                )
                new_student.save()

    def extractData(self):
        """Drive method to extract, validate, and populate data."""
        submission_count = len(os.listdir(self.__dirName))

        for _ in range(math.ceil(submission_count / 2)):
            try:
                self.__extractStudentFilesFromZIP()
                self.__extractJSON()
                self.__extractMetaDataFromCSV()
                self.__verifyStudentSubmissionExists()
                self.__verifyStudentUserExistsInMetaData()
            except Exception:
                CodeGradeDataIngestion.allErrors.extend(self.__errors)
                self.__errors = []
                continue
            self.__populateDatabase()

        if CodeGradeDataIngestion.allErrors:
            DataIngestionError.createErrorJSON(
                "codegrade_data_errors",
                CodeGradeDataIngestion.allErrors,
            )
            CodeGradeDataIngestion.allErrors = []
            CodeGradeDataIngestion.fileSeen = set()


def main():
    """Run the CodeGrade ingestion pipeline."""
    cg_data = CodeGradeDataIngestion("codegrade_data")
    cg_data.extractData()


if __name__ == "__main__":
    main()
