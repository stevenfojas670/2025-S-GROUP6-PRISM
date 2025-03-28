"""
Created by Daniel Levy, 3/17/2025

This script is responsible for the data ingestion of
Canvas metadata into the database. We are primarily
concerned with models from the `courses` app. We will also
manually validate that there are no errors in the provided
Canvas gradebook files.
"""

# Django setup
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prism_backend.settings")
django.setup()

import pandas as pd
from data_ingestion.errors.DataIngestionError import DataIngestionError
import data_ingestion.errors.DataIngestionErrorBuilder as eb
from courses.models import Semester, Class


class CanvasDataIngestion:

    # Fields
    __dirName = None  # Directory where Canvas data is located
    __fileName = None  # Current file we are checking
    __data = None  # Dataframe to store file contents
    __course = None
    __section = None
    __year = None
    __semester = None  # Spring, Summer, or Fall
    __metaID = None  # List of Canvas metadata info
    __courseID = None  # Course ID: Last number in the metaID
    __errors = None  # List of errors

    errors = list()  # Static list to keep track of all errors

    # Methods
    def __init__(self, dirName):
        self.__dirName = dirName
        self.__fileName = ""
        self.__data = ""
        self.__course = ""
        self.__section = ""
        self.__year = ""
        self.__semester = ""
        self.__metaID = list()
        self.__courseID = ""
        self.__errors = list()

    """
        This method will parse the file name and extract
        the info related to the Canvas course, so we may
        validate each student's Canvas meta ID.
    """

    def __parseCanvasFileName(self, file):
        fields = file.split("-")

        courseInfo = fields[3].split("_")
        self.__course = courseInfo[0] + courseInfo[1]
        self.__section = courseInfo[2]

        semesterInfo = fields[4].split("_")
        self.__year = semesterInfo[1]
        self.__semester = semesterInfo[2].removesuffix(".csv")
        self.__fileName = file

    """
        Here, we are going to take our .csv file and extract the info
        into a Pandas dataframe so we can use it
    """

    def __convertToDataFrame(self):
        csvFile = open(f"{self.__dirName}/{self.__fileName}", "r")
        self.__data = pd.read_csv(csvFile)
        csvFile.close()

    """
        This will be our main error handling method that will check
        if all the individual student entries in the .csv file match
        the expected data for the Canvas course.
    """

    def __validateData(self):
        self.__metaID = self.__data["Section"].iloc[0]
        rowCount = 1
        for index, student in self.__data.iterrows():
            studentNameFields = student["Student"].split(",")
            studentName = studentNameFields[1][1:] + " " + studentNameFields[0]
            # Error Check #1: Make sure the student's User/login ID
            #                 match (it should be their ACE ID)
            if student["SIS User ID"] != student["SIS Login ID"]:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(
                        f"The User ID for {studentName} does not " "match the Login ID"
                    )
                    .createError()
                )

            self.courseInfo = self.__getCourseMetaData(student["Section"], rowCount)

            # Error Check #2: Make sure the semester matches the semester
            #                 given in the file name
            if self.courseInfo[0] != self.__semester:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(
                        f"The semester for {studentName} does not "
                        "match the Canvas semester."
                    )
                    .createError()
                )

            # Error Check #3: Make sure the course matches the course
            #                 given in the file name
            if self.courseInfo[1] != self.__course:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(
                        f"The course name for {studentName} does not "
                        "match the Canvas course name."
                    )
                    .createError()
                )

            # Error Check #4: Make sure the section matches the section
            #                 given in the file name
            if self.courseInfo[2] != self.__section:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(
                        f"The section number for {studentName} does not "
                        "match the Canvas section."
                    )
                    .createError()
                )

            # Error Check #5: Make sure the Canvas meta ID matches the
            #                 meta ID for the first student in the file
            if student["Section"] != self.__metaID:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The Canvas metadata ID does not match for {studentName}.")
                    .createError()
                )

            rowCount += 1

    """
        When we are trying to validate the student data, we must parse
        the Canvas meta ID per student to make sure each part of the ID
        matches the provided information in the title of the .csv file
    """

    def __getCourseMetaData(self, metaID, row):
        courseInfo = metaID.split("-")
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
            self.__errors.append(
                eb.DataIngestionErrorBuilder()
                .addFileName(self.__fileName)
                .addLine(row)
                .addMsg(f"The semester is invalid.")
                .createError()
            )

        metaData.append(courseInfo[1] + courseInfo[2])
        metaData.append(courseInfo[3][3:])
        metaData.append(courseInfo[4])

        self.__courseID = courseInfo[4]
        return metaData

    """
        This method will populate the database based on the data from
        the Canvas gradebook.

        Table We Populate: Semester, Course
        We can not populate Professor/ProfessorCourse yet since we do
        not have access to the professor information from the Canvas
        gradebook.
    """

    def __populateDatabase(self):

        # First, add new entry for Semester
        try:
            semester = Semester.objects.get_or_create(
                name=self.__semester + self.__year
            )
        except Semester.DoesNotExist:
            semester = Semester(name=self.__semester + self.__year)
            semester.save()

        # Then, add new entry for Course
        try:
            className = Class.objects.get_or_create(name=self.__course)
        except Class.DoesNotExist:
            className = Class(name=self.__course)
            className.save()

    """
        This will be the main method that a user will call to extract
        all information from the exported Canvas gradebook file.
    """

    def extractData(self):
        for file in os.listdir(self.__dirName):

            # Error Check #1: Make sure each file in the canvas_data
            #                 directory is indeed a .csv file
            if not file.endswith(".csv"):
                self.errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(file)
                    .addMsg(f"The file '{file}' is not a valid .csv file.")
                    .createError()
                )
                continue

            self.__parseCanvasFileName(file)
            self.__convertToDataFrame()
            self.__validateData()

            if len(self.__errors) > 0:
                for e in self.__errors:
                    self.errors.append(e)
                self.__errors = list()
                continue

            self.__populateDatabase()

        if (len(CanvasDataIngestion.errors)) > 0:
            DataIngestionError.createErrorJSON(
                "canvas_data_errors", CanvasDataIngestion.errors
            )
            CanvasDataIngestion.errors = list()


"""
    Main method to interface with script
"""


def main():
    ingest = CanvasDataIngestion("canvas_data")
    ingest.extractData()


if __name__ == "__main__":
    main()
