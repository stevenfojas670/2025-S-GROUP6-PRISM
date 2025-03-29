"""Created by Daniel Levy, 3/17/2025.

This script handles the ingestion of Canvas gradebook metadata into the database.
It validates .csv data and populates the `courses` app models accordingly.
"""

import os
import django
import pandas as pd

from data_ingestion.errors.DataIngestionError import DataIngestionError
import data_ingestion.errors.DataIngestionErrorBuilder as eb
from courses.models import Semester, Class

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prism_backend.settings")
django.setup()


class CanvasDataIngestion:
    """Handle ingestion and validation of Canvas gradebook .csv files."""

    __dirName = None
    __fileName = None
    __data = None
    __course = None
    __section = None
    __year = None
    __semester = None
    __metaID = None
    __courseID = None
    __errors = None

    errors = []

    def __init__(self, dirName):
        """Initialize the ingestion class with the Canvas data directory."""
        self.__dirName = dirName
        self.__fileName = ""
        self.__data = ""
        self.__course = ""
        self.__section = ""
        self.__year = ""
        self.__semester = ""
        self.__metaID = []
        self.__courseID = ""
        self.__errors = []

    def __parseCanvasFileName(self, file):
        """Parse Canvas filename to extract course metadata."""
        fields = file.split("-")
        courseInfo = fields[3].split("_")
        self.__course = courseInfo[0] + courseInfo[1]
        self.__section = courseInfo[2]
        semesterInfo = fields[4].split("_")
        self.__year = semesterInfo[1]
        self.__semester = semesterInfo[2].removesuffix(".csv")
        self.__fileName = file

    def __convertToDataFrame(self):
        """Convert CSV file contents to a Pandas DataFrame."""
        csv_path = os.path.join(self.__dirName, self.__fileName)
        with open(csv_path, "r") as csvFile:
            self.__data = pd.read_csv(csvFile)

    def __validateData(self):
        """Validate students' metadata entries against file metadata."""
        self.__metaID = self.__data["Section"].iloc[0]
        rowCount = 1

        for _, student in self.__data.iterrows():
            studentNameFields = student["Student"].split(",")
            studentName = studentNameFields[1].strip() + " " + studentNameFields[0]

            if student["SIS User ID"] != student["SIS Login ID"]:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The User ID for {studentName} does not match the Login ID.")
                    .createError()
                )

            self.courseInfo = self.__getCourseMetaData(student["Section"], rowCount)

            if self.courseInfo[0] != self.__semester:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The semester for {studentName} does not match Canvas data.")
                    .createError()
                )

            if self.courseInfo[1] != self.__course:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The course for {studentName} does not match Canvas data.")
                    .createError()
                )

            if self.courseInfo[2] != self.__section:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The section for {studentName} does not match Canvas data.")
                    .createError()
                )

            if student["Section"] != self.__metaID:
                self.__errors.append(
                    eb.DataIngestionErrorBuilder()
                    .addFileName(self.__fileName)
                    .addLine(rowCount)
                    .addMsg(f"The Canvas metadata ID does not match for {studentName}.")
                    .createError()
                )

            rowCount += 1

    def __getCourseMetaData(self, metaID, row):
        """Parse Canvas metaID into semester, course name, section, and ID."""
        courseInfo = metaID.split("-")
        metaData = []

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
                .addMsg("The semester is invalid.")
                .createError()
            )

        metaData.append(courseInfo[1] + courseInfo[2])
        metaData.append(courseInfo[3][3:])
        metaData.append(courseInfo[4])
        self.__courseID = courseInfo[4]
        return metaData

    def __populateDatabase(self):
        """Insert Semester and Course records into the database."""
        try:
            Semester.objects.get_or_create(name=self.__semester + self.__year)
        except Semester.DoesNotExist:
            Semester(name=self.__semester + self.__year).save()

        try:
            Class.objects.get_or_create(name=self.__course)
        except Class.DoesNotExist:
            Class(name=self.__course).save()

    def extractData(self):
        """Extract and validate all Canvas .csv files in the directory."""
        for file in os.listdir(self.__dirName):
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

            if self.__errors:
                self.errors.extend(self.__errors)
                self.__errors = []
                continue

            self.__populateDatabase()

        if CanvasDataIngestion.errors:
            DataIngestionError.createErrorJSON(
                "canvas_data_errors",
                CanvasDataIngestion.errors,
            )
            CanvasDataIngestion.errors = []


def main():
    """Run the Canvas data ingestion pipeline."""
    ingest = CanvasDataIngestion("canvas_data")
    ingest.extractData()


if __name__ == "__main__":
    main()
