"""Created by Daniel Levy, 3/17/2025.

This script is responsible for the data ingestion of
Canvas metadata into the database. We are primarily
concerned with models from the `courses` app. We will also
manually validate that there are no errors in the provided
Canvas gradebook files.
"""

# Django setup
import os
import django

import pandas as pd
from data_ingestion.errors.DataIngestionError import DataIngestionError
import data_ingestion.errors.DataIngestionErrorBuilder as eb
from courses.models import Semester, Class

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prism_backend.settings")
django.setup()


class CanvasDataIngestion:
    """CanvasDataIngestion is a class designed to handle the ingestion and
    validation of Canvas gradebook data. It processes .csv files containing
    student information, validates the data against expected metadata, and
    populates the database with relevant information.

    Attributes:
        __dirName (str): Directory where Canvas data is located.
        __fileName (str): Current file being processed.
        __data (pd.DataFrame): Dataframe to store file contents.
        __course (str): Course name extracted from the file name.
        __section (str): Section number extracted from the file name.
        __year (str): Year extracted from the file name.
        __semester (str): Semester (Spring, Summer, or Fall) extracted from the file name.
        __metaID (list): List of Canvas metadata information.
        __courseID (str): Course ID extracted from the metadata.
        __errors (list): List of errors encountered during validation.
        errors (list): Static list to keep track of all errors across instances.

    Methods:
        __init__(dirName):
            Initializes the CanvasDataIngestion instance with the directory name.

        __parseCanvasFileName(file):
            Parses the file name to extract course, section, year, and semester information.

        __convertToDataFrame():
            Converts the .csv file into a Pandas dataframe for processing.

        __validateData():
            Validates the student data in the .csv file against the expected metadata.

        __getCourseMetaData(metaID, row):
            Parses the Canvas meta ID to extract semester, course, section, and other metadata.

        __populateDatabase():
            Populates the database with semester and course information based on the Canvas data.

        extractData():
            Main method to process all .csv files in the specified directory, validate the data,
            and populate the database. Also handles error reporting for invalid files or data.
    """

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
        """Initializes an instance of the class with the specified directory
        name and sets up default values for various attributes.

        Args:
            dirName (str): The name of the directory to be used for data ingestion.

        Attributes:
            __dirName (str): The directory name provided during initialization.
            __fileName (str): The name of the file to be processed (default is an empty string).
            __data (str): The data content to be processed (default is an empty string).
            __course (str): The course name or identifier (default is an empty string).
            __section (str): The section identifier (default is an empty string).
            __year (str): The year associated with the data (default is an empty string).
            __semester (str): The semester associated with the data (default is an empty string).
            __metaID (list): A list to store metadata IDs (default is an empty list).
            __courseID (str): The course ID (default is an empty string).
            __errors (list): A list to store error messages (default is an empty list).
        """
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
        """Parses the Canvas file name to extract course, section, semester,
        and year information.

        Args:
            file (str): The name of the file to be parsed. The file name is expected to follow
                        a specific format with fields separated by hyphens ('-') and underscores ('_').

        Attributes Set:
            self.__course (str): The course identifier extracted from the file name.
            self.__section (str): The section identifier extracted from the file name.
            self.__year (str): The year extracted from the file name.
            self.__semester (str): The semester extracted from the file name.
            self.__fileName (str): The original file name passed to the method.

        Raises:
            IndexError: If the file name does not follow the expected format and required fields
                        are missing.
        """
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
        """Converts the contents of a CSV file into a Pandas DataFrame and
        stores it in the `__data` attribute.

        This method reads the CSV file specified by the `__dirName` and `__fileName` attributes,
        loads its contents into a Pandas DataFrame, and assigns it to the `__data` attribute.
        The file is opened in read mode and closed after reading.

        Raises:
            FileNotFoundError: If the specified CSV file does not exist.
            pd.errors.EmptyDataError: If the CSV file is empty.
            pd.errors.ParserError: If there is an error parsing the CSV file.
        """
        csvFile = open(f"{self.__dirName}/{self.__fileName}", "r")
        self.__data = pd.read_csv(csvFile)
        csvFile.close()

    """
        This will be our main error handling method that will check
        if all the individual student entries in the .csv file match
        the expected data for the Canvas course.
    """

    def __validateData(self):
        """Validates the data in the provided dataset by performing a series of
        error checks. Errors encountered during validation are appended to the
        `__errors` list.

        Validation Steps:
        1. Ensures that the "SIS User ID" matches the "SIS Login ID" for each student.
        2. Verifies that the semester in the data matches the semester specified in the file name.
        3. Confirms that the course name in the data matches the course name specified in the file name.
        4. Checks that the section number in the data matches the section number specified in the file name.
        5. Ensures that the Canvas metadata ID for each student matches the metadata ID of the first student.

        Raises:
            DataIngestionError: If any of the validation checks fail, an error is created
                                using the `DataIngestionErrorBuilder` and added to the `__errors` list.

        Attributes:
            __metaID (str): The metadata ID of the first student in the dataset.
            __errors (list): A list to store all validation errors encountered.
            courseInfo (tuple): Metadata about the course, including semester, course name, and section.

        Notes:
            - The method assumes that the dataset is stored in `self.__data` as a pandas DataFrame.
            - The file name, semester, course, and section are expected to be stored in `self.__fileName`,
              `self.__semester`, `self.__course`, and `self.__section` respectively.
            - The `__getCourseMetaData` method is used to retrieve course metadata for validation.
        """
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

            self.courseInfo = self.__getCourseMetaData(
                student["Section"], rowCount)

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
                    .addMsg(
                        f"The Canvas metadata ID does not match " f"for {studentName}."
                    )
                    .createError()
                )

            rowCount += 1

    """
        When we are trying to validate the student data, we must parse
        the Canvas meta ID per student to make sure each part of the ID
        matches the provided information in the title of the .csv file
    """

    def __getCourseMetaData(self, metaID, row):
        """Extracts and processes metadata for a course based on the provided
        Canvas meta ID.

        Args:
            metaID (str): The Canvas meta ID string containing course information.
            row (int): The row number in the data source, used for error reporting.

        Returns:
            list: A list containing the following course metadata:
                - Semester (e.g., "Sprg", "Sumr", "Fall").
                - Concatenated course identifier (e.g., courseInfo[1] + courseInfo[2]).
                - Course year (e.g., extracted from courseInfo[3]).
                - Course ID (e.g., courseInfo[4]).

        Raises:
            Appends a DataIngestionError to the internal error list if the semester
            information in the meta ID is invalid.

        Notes:
            - The semester is determined by the last digit of the first field in the meta ID:
                - "2" corresponds to "Sprg" (Spring).
                - "5" corresponds to "Sumr" (Summer).
                - "8" corresponds to "Fall".
            - If the semester is invalid, an error is logged with details about the file
              name and row number.
        """
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
        """Populates the database with Semester and Course information.

        This method performs the following actions:
        1. Adds a new entry for the Semester if it does not already exist.
        2. Adds a new entry for the Course if it does not already exist.

        Attributes:
            self.__semester (str): The name of the semester (e.g., "Fall").
            self.__year (str): The year of the semester (e.g., "2025").
            self.__course (str): The name of the course to be added.

        Exceptions:
            Semester.DoesNotExist: Raised if the Semester object does not exist.
            Class.DoesNotExist: Raised if the Class object does not exist.
        """

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
        """Extracts and processes data from files in the specified directory.

        This method iterates through all files in the directory specified by `self.__dirName`.
        It performs the following steps for each file:
        1. Checks if the file is a valid `.csv` file. If not, logs an error and skips the file.
        2. Parses the file name to extract relevant information.
        3. Converts the file content into a DataFrame.
        4. Validates the data in the DataFrame.
        5. If validation passes, populates the database with the data.
           Otherwise, logs validation errors and skips the file.

        Additionally, if any errors are encountered during the process, they are logged
        and saved as a JSON file named `canvas_data_errors`.

        Errors are tracked using the `self.errors` list and a class-level `CanvasDataIngestion.errors` list.

        Raises:
            DataIngestionError: If any errors occur during the data ingestion process.
        """
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
    """Main function to initiate the Canvas data ingestion process.

    This function creates an instance of the `CanvasDataIngestion` class with the
    specified data source and calls its `extractData` method to extract data from Canvas.

    Usage:
        This function serves as the entry point for the data ingestion process.

    Dependencies:
        - CanvasDataIngestion: A class responsible for handling Canvas data ingestion.

    Raises:
        Ensure that the `CanvasDataIngestion` class and its `extractData` method are
        properly implemented and accessible.
    """
    ingest = CanvasDataIngestion("canvas_data")
    ingest.extractData()


if __name__ == "__main__":
    main()
