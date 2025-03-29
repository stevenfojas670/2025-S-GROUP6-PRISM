"""Created by Daniel Levy, 2/21/2025.

This script is responsible for the data ingestion of
CodeGrade metadata into the database. We are primarily
concerned with models from the `assignments` app. We will also
manually validate that there are no errors in the provided
CodeGrade data files.
"""

# Django setup
from assignments.models import Student, Assignment, Submission
import data_ingestion.errors.DataIngestionErrorBuilder as eb
from data_ingestion.errors.DataIngestionError import DataIngestionError
import json
import math
import pandas as pd
from zipfile import ZipFile
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prism_backend.settings")
django.setup()


class CodeGradeDataIngestion:
    """CodeGradeDataIngestion.

    This class is responsible for handling the ingestion of CodeGrade data,
    including extracting student submissions, validating metadata, and populating
    the database with the extracted information. It performs various checks to
    ensure the integrity and completeness of the data.

    Attributes:
        __dirName (str): Directory containing all data (should be 'codegrade_data').
        __submissionFileName (str): Current course/assignment being processed.
        __className (str): Name of the class extracted from the ZIP file.
        __section (str): Section of the class extracted from the ZIP file.
        __semester (str): Semester information extracted from the ZIP file.
        __assignmentName (str): Assignment name extracted from the ZIP file.
        __zipFileDirectory (str): Directory containing unzipped student submissions.
        __submissions (list): List of CodeGrade submission IDs.
        __users (list): List of CodeGrade user IDs.
        __metaData (DataFrame): Dataframe containing CodeGrade metadata.
        __errors (list): List of errors encountered during data ingestion.
        fileSeen (set): Static set tracking all processed ZIP files.
        allErrors (list): Static list tracking all errors encountered.

    Methods:
        __init__(dirName):
            Initializes the CodeGradeDataIngestion object with the given directory name.

        __extractStudentFilesFromZIP():
            Extracts the next ZIP file from the directory and processes student submissions.
            Raises an error if no valid ZIP file is found.

        __parseZipFileName(name):
            Parses the ZIP file name to extract class, section, semester, and assignment details.

        __checkIfJSONFileExists():
            Checks if the .cg-info.json file exists in the extracted ZIP directory.
            Logs an error if the file is missing.

        __extractJSON():
            Extracts submission and user data from the .cg-info.json file.

        __extractMetaDataFromCSV():
            Extracts metadata from the corresponding CSV file for the current ZIP file.
            Logs an error if the CSV file is missing.

        __verifyStudentSubmissionExists():
            Verifies that each submission ID corresponds to a valid student submission in the ZIP directory.

        __verifyStudentUserExistsInMetaData():
            Verifies that each user ID in the metadata corresponds to exactly one submission
            and matches the appropriate student name.

        __checkIfStudentFileExists(fileName):
            Checks if a student's submission directory exists in the ZIP directory.
            Returns the submission ID and student name if valid, otherwise logs an error.

        __populateDatabase():
            Populates the database with student information extracted from the metadata.

        extractData():
            Main method responsible for parsing, validating, and processing all CodeGrade data.
            Handles errors and generates a JSON file for any errors encountered.
    """

    # Fields
    # Directory containing all data (should be 'codegrade_data')
    __dirName = None
    __submissionFileName = None  # Current course/assignment we are checking data for
    __className = None
    __section = None
    __semester = None
    __assignmentName = None
    __zipFileDirectory = None  # Directory that contains unzipped student submissions
    __submissions = None  # List of CodeGrade submission IDs
    __users = None  # List of CodeGrade user IDs
    __metaData = None  # Dataframe containing CodeGrade meta data
    __errors = None

    fileSeen = set()  # Static set that keeps track of every file seen
    allErrors = list()  # Static list that keeps track of all errors found

    # Methods
    def __init__(self, dirName):
        """Initializes an instance of the class with the specified directory
        name and sets up default values for various attributes.

        Args:
            dirName (str): The name of the directory to be used for data processing.

        Attributes:
            __dirName (str): The directory name provided during initialization.
            __submissionFileName (str): The name of the submission file (default is an empty string).
            __className (str): The name of the class (default is an empty string).
            __section (str): The section of the class (default is an empty string).
            __semester (str): The semester information (default is an empty string).
            __assignmentName (str): The name of the assignment (default is an empty string).
            __zipFileDirectory (str): The directory for zip files (default is an empty string).
            __submissions (list): A list to store submission data (default is an empty list).
            __users (list): A list to store user data (default is an empty list).
            __metaData (list): A list to store metadata (default is an empty list).
            __errors (list): A list to store error messages (default is an empty list).
        """
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

    """
        This method will check the current directory and find the next ZIP
        file to extract and check the student submissions for.
    """

    def __extractStudentFilesFromZIP(self):
        """Extracts student submission files from ZIP archives located in the
        specified directory.

        This method iterates through all files in the directory specified by `self.__dirName`.
        It identifies ZIP files that have not been processed yet (not in `CodeGradeDataIngestion.fileSeen`),
        parses their names, and extracts their contents into a designated subdirectory.

        If no new ZIP files are found or if duplicate ZIP files are detected, an error is logged
        and a `ValueError` is raised.

        Raises:
            ValueError: If no new ZIP files are found or if duplicate ZIP files are detected.

        Side Effects:
            - Extracts ZIP file contents into a subdirectory.
            - Updates the `CodeGradeDataIngestion.fileSeen` set with the processed ZIP file name.
            - Appends an error to `self.__errors` if an issue is encountered.
        """
        for file in os.listdir(self.__dirName):
            if file.endswith(
                    ".zip") and file not in CodeGradeDataIngestion.fileSeen:
                self.__parseZipFileName(file)
                self.__zipFileDirectory = (
                    f"{self.__dirName}/{self.__submissionFileName}"
                )

                zipFile = ZipFile(f"{self.__dirName}/{file}")
                zipFile.extractall(self.__zipFileDirectory)

                CodeGradeDataIngestion.fileSeen.add(file)
                return

        # ERROR CHECK #1: If we reach this point,
        # then we either have a duplicated
        # ZIP file in the directory or there are no
        # ZIP files in the directory, so we have to create an error
        self.__errors.append(
            eb.DataIngestionErrorBuilder()
            .addFileName(self.__dirName)
            .addMsg(
                f"A duplicate .zip file was found containing student "
                f"submission in {self.__dirName}"
            )
            .createError()
        )
        raise ValueError()

    """
        CodeGrade exports a ZIP file with the following title format:
            '<CS Class> <Section> - <Semester> <Assignment Name>'

        This method will simply parse the title and save each part to
        the object's appropriate fields. No error handling is needed.
    """

    def __parseZipFileName(self, name):
        """Parses the given zip file name to extract and set class-related
        attributes.

        Args:
            name (str): The name of the zip file to parse. Expected format:
                        "<Class Name> <Section>-<Semester>-<Assignment Name>.zip"

        Attributes Set:
            __submissionFileName (str): The name of the submission file without the ".zip" extension.
            __className (str): The class name extracted from the file name.
            __section (str): The section of the class extracted from the file name.
            __semester (str): The semester information extracted from the file name.
            __assignmentName (str): The assignment name extracted from the file name.
        """
        self.__submissionFileName = name.removesuffix(".zip")
        zipFields = name.split("-", 2)

        canvasName = zipFields[0].split(" ")
        self.__className = canvasName[0] + " " + canvasName[1]
        self.__section = canvasName[2]

        self.__semester = zipFields[1].strip()
        self.__assignmentName = zipFields[2][:-4].strip()

    """
        Every exported CodeGrade ZIP file will contain a .cg-info.json file
        that keeps track of all submissions and users. This is needed to
        ensure data authentication, so it must be present in the file.
    """

    def __checkIfJSONFileExists(self):
        """Checks if the .cg-info.json file exists in the specified directory.

        If the file does not exist, an error is appended to the internal errors list
        indicating that the .cg-info.json file is missing.

        Raises:
            DataIngestionError: If the .cg-info.json file is not found in the directory.
        """
        if not os.path.exists(f"{self.__zipFileDirectory}/.cg-info.json"):
            self.__errors.append(
                eb.DataIngestionErrorBuilder()
                .addFileName(self.__dirName)
                .addMsg("The .cg-info.json file is missing.")
                .createError()
            )

    """
        Once the ZIP file has been extracted, we can now take the json
        data and populate the submissions/users fields.
    """

    def __extractJSON(self):
        """Extracts and processes JSON data from a CodeGrade information file.

        This method checks if the required JSON file exists in the specified directory.
        It then opens and loads the JSON file, extracting submission IDs and user IDs
        into the instance variables `__submissions` and `__users`.

        Raises:
            FileNotFoundError: If the `.cg-info.json` file does not exist in the specified directory.
            JSONDecodeError: If the JSON file is not properly formatted.
        """
        self.__checkIfJSONFileExists()

        cgInfo = open(f"{self.__zipFileDirectory}/.cg-info.json", "r")
        jsonStudentData = json.load(cgInfo)

        self.__submissions, self.__users = (
            jsonStudentData["submission_ids"],
            jsonStudentData["user_ids"],
        )

    """
        This method handles the extraction of CodeGrade metadata for
        each student which is exported through a CSV file.
    """

    def __extractMetaDataFromCSV(self):
        """Extracts metadata from a CSV file located in the specified
        directory.

        This method searches for a CSV file in the directory specified by `self.__dirName`
        that matches the name of `self.__submissionFileName`. If the file is found, it is
        read into a pandas DataFrame and stored in `self.__metaData`. If the file is not
        found, an error is logged and a `ValueError` is raised.

        Raises:
            ValueError: If the specified CSV file is not found in the directory.

        Side Effects:
            - Updates `self.__metaData` with the contents of the CSV file if found.
            - Appends an error to `self.__errors` if the file is not found.
        """
        for file in os.listdir(self.__dirName):
            if file == f"{self.__submissionFileName}.csv":
                csvFile = open(f"{self.__dirName}/{file}", "r")
                df = pd.read_csv(csvFile)
                csvFile.close()
                self.__metaData = df
                return

        # ERROR CHECK #1: If we could not find the appropriate
        # metadata .csv file for the current ZIP file we extracted,
        # generate an error
        self.__errors.append(
            eb.DataIngestionErrorBuilder()
            .addFileName(self.__submissionFileName)
            .addMsg(
                f"{self.__submissionFileName}.csv was not found "
                f"in {self.__dirName}."
            )
            .createError()
        )
        raise ValueError()

    """
        Here, we verify that every submission ID is linked back to a student.
        We check the ZIP directory to make sure the submission is there and
        ensure the student name matches the name associated with the given
        submission.
    """

    def __verifyStudentSubmissionExists(self):
        """Verifies the existence and correctness of student submissions.

        This method iterates through the submissions dictionary and checks if
        the student file exists for each key. If a submission file is found,
        it validates that the submission ID matches the expected value for
        the current student. If any discrepancies are found, an error is
        logged with details about the issue.

        Errors are appended to the `__errors` list in the form of
        `DataIngestionError` objects.

        Raises:
            Exception: If an error occurs during the file existence check,
                       it is caught and the iteration continues.

        Error Conditions:
            - Submission ID does not match the expected value for a student.

        Attributes:
            __submissions (dict): A dictionary where keys represent student
                                  identifiers and values represent expected
                                  submission IDs.
            __errors (list): A list to store error objects for any issues
                             encountered during verification.
            __zipFileDirectory (str): The directory path of the zip file
                                      being processed.

        Dependencies:
            - `self.__checkIfStudentFileExists(key)`: Checks if a student file
              exists and returns the submission ID and student name.
            - `eb.DataIngestionErrorBuilder`: Used to construct error objects
              with detailed information.
        """
        for key, value in self.__submissions.items():
            try:
                subID, studentName = self.__checkIfStudentFileExists(key)
            except BaseException:
                continue
            else:
                # ERROR CHECK #1: Make sure the submission ID matches
                # for the current student
                if subID != value:
                    self.__errors.append(
                        eb.DataIngestionErrorBuilder()
                        .addFileName(self.__zipFileDirectory)
                        .addMsg(
                            f"The submission ID #{subID} "
                            f"for {studentName} is not correct."
                        )
                        .createError()
                    )

    """
        Similarly, we check to make sure that each user ID in the metadata
        corresponds to exactly one submission, and that submission matches
        the appropriate student name.
    """

    def __verifyStudentUserExistsInMetaData(self):
        """
        Verifies that each student user in the internal `__users` dictionary has valid
        metadata associated with them in the `__metaData` DataFrame. Performs the following
        checks for each user:

        1. Ensures the student has a valid submission by checking if their user ID exists
           in the metadata. If no metadata is found, an error is logged, and a ValueError
           is raised.
        2. Ensures the student does not have multiple metadata entries. If multiple entries
           are found, an error is logged, and a ValueError is raised.
        3. Ensures the student name matches the name in the metadata file. If there is a
           mismatch, an error is logged, and a ValueError is raised.

        Errors encountered during these checks are appended to the `__errors` list using
        the `DataIngestionErrorBuilder`.

        Raises:
            ValueError: If any of the above checks fail.
        """
        for key, value in self.__users.items():

            try:
                subID, studentName = self.__checkIfStudentFileExists(key)
            except BaseException:
                raise ValueError()
            else:

                entry = self.__metaData.loc[self.__metaData["Id"] == value]
                entriesFound = len(entry)

                # ERROR CHECK #1: Make sure the current
                # student has a valid submission
                if entriesFound < 1:
                    self.__errors.append(
                        eb.DataIngestionErrorBuilder()
                        .addFileName(self.__submissionFileName)
                        .addMsg(
                            f"User ID {value} does not have any "
                            f"metadata associated with it."
                        )
                        .createError()
                    )
                    raise ValueError()

                # ERROR CHECK #2: Make sure the current student
                # does not have multiple submissions
                elif entriesFound > 1:
                    self.__errors.append(
                        eb.DataIngestionErrorBuilder()
                        .addFileName(self.__submissionFileName)
                        .addMsg(
                            f"User ID {value} has multiple metadata "
                            f"entries associated with it."
                        )
                        .createError()
                    )
                    raise ValueError()

                # ERROR CHECK #3: Make sure the student name matches
                # the name in the user ID portion of cg_data.json
                if entry.iloc[0, 2] != studentName:
                    self.__errors.append(
                        eb.DataIngestionErrorBuilder()
                        .addFileName(self.__submissionFileName)
                        .addMsg(
                            f"User ID {value} does not match the "
                            f"given name in the metadata file."
                        )
                        .createError()
                    )
                    raise ValueError()

    """
        For this helper method, we are checking whether or not
        a student has a directory inside the ZIP directory that
        contains their submitted code files to CodeGrade.
    """

    def __checkIfStudentFileExists(self, fileName):
        """Checks if a student's submission file exists in the ZIP directory.

        Args:
            fileName (str): The name of the student's submission file in the format
                            "<submissionID>-<studentName>".

        Returns:
            tuple: A tuple containing:
                - subID (int): The submission ID extracted from the file name.
                - studentName (str): The student's name extracted from the file name.

        Raises:
            ValueError: If the student's submission file is not found in the ZIP directory.

        Side Effects:
            - Appends an error to the `__errors` list if the file is missing, using
              `DataIngestionErrorBuilder` to construct the error message.
        """
        subID, studentName = fileName.split("-", 1)
        studentName = studentName.strip()

        subID = int(subID.strip())

        # ERROR CHECK #1: Make sure the student
        # has a submission in the ZIP directory
        if fileName not in os.listdir(self.__zipFileDirectory):
            self.__errors.append(
                eb.DataIngestionErrorBuilder()
                .addFileName(self.__submissionFileName)
                .addMsg(
                    f"Submission for {studentName} " f"is missing in zip directory."
                )
                .createError()
            )
            raise ValueError()

        return subID, studentName

    """
        This method will populate the database by inserting
        a new entry for each student.
    """

    def __populateDatabase(self):
        """Populates the database with student information from the metadata.

        This method iterates through the metadata and adds new student entries to the database.
        Each student is identified by their unique CodeGrade ID and username. If a student
        already exists in the database, it ensures the student is retrieved or created.

        Steps:
        1. Splits the student's full name into first and last names.
        2. Attempts to retrieve or create a Student object in the database using the provided
           metadata fields such as email, CodeGrade ID, username, first name, and last name.
        3. If the student does not exist, creates a new Student object and saves it to the database.

        Raises:
            Student.DoesNotExist: If the student cannot be found in the database during retrieval.

        Attributes:
            self.__metaData (DataFrame): A pandas DataFrame containing student metadata with
                                         columns such as "Name", "Username", and "Id".

        Note:
            - The email is constructed by appending "@unlv.nevada.edu" to the student's username.
            - Assumes that the "Name" field in the metadata contains both first and last names
              separated by a space.
        """

        # First, add new entry for Semester
        for index, student in self.__metaData.iterrows():
            names = student["Name"].split(" ")

            # Add new Student to database
            try:
                currStudent = Student.objects.get_or_create(
                    email=student["Username"] + "@unlv.nevada.edu",
                    codeGrade_id=student["Id"],
                    username=student["Username"],
                    first_name=names[0],
                    last_name=names[1],
                )
            except Student.DoesNotExist:
                currStudent = Student(
                    email=student["Username"] + "@unlv.nevada.edu",
                    codeGrade_id=student["Id"],
                    username=student["Username"],
                    first_name=names[0],
                    last_name=names[1],
                )
                currStudent.save()

    """
        This is main method that is responsible for parsing
        and validating all CodeGrade data.
    """

    def extractData(self):
        """Extracts and processes student submission data from a specified
        directory.

        This method iterates through student submission files, performing the following steps:
        1. Extracts student files from ZIP archives.
        2. Extracts JSON data.
        3. Extracts metadata from CSV files.
        4. Verifies that student submissions exist.
        5. Verifies that student users exist in the metadata.

        If any errors occur during these steps, they are collected and added to a global error list.
        After processing all submissions, any accumulated errors are written to a JSON file.

        Additionally, if no errors occur during the processing of a submission, the data is populated into the database.

        Raises:
            Exceptions are caught and handled internally. Errors are logged and stored in a JSON file.

        Side Effects:
            - Updates the global error list `CodeGradeDataIngestion.allErrors`.
            - Writes errors to a JSON file if any are encountered.
            - Populates the database with valid submission data.

        Note:
            The method processes submissions in batches, iterating over half the number of files in the directory.
        """
        submissionDirLength = len(os.listdir(self.__dirName))

        for i in range(math.ceil(submissionDirLength / 2)):
            try:
                self.__extractStudentFilesFromZIP()
                self.__extractJSON()
                self.__extractMetaDataFromCSV()
                self.__verifyStudentSubmissionExists()
                self.__verifyStudentUserExistsInMetaData()
            except BaseException:
                for e in self.__errors:
                    CodeGradeDataIngestion.allErrors.append(e)
                self.__errors = list()
                continue
            else:
                self.__populateDatabase()

        if len(CodeGradeDataIngestion.allErrors) > 0:
            DataIngestionError.createErrorJSON(
                "codegrade_data_errors", CodeGradeDataIngestion.allErrors
            )
            CodeGradeDataIngestion.allErrors = list()
            CodeGradeDataIngestion.fileSeen = set()


def main():
    """Main function to initiate the CodeGrade data ingestion process.

    This function creates an instance of the `CodeGradeDataIngestion` class
    with the specified data source and calls its `extractData` method to
    perform the data extraction.

    Usage:
        Call this function to start the data ingestion process for CodeGrade.

    Raises:
        Any exceptions raised during the instantiation of `CodeGradeDataIngestion`
        or the execution of the `extractData` method will propagate to the caller.
    """
    cgData = CodeGradeDataIngestion("codegrade_data")
    cgData.extractData()


if __name__ == "__main__":
    main()
