"""Created by Daniel Levy, 3/26/2025.

This is a unit test script for "extractCodeGradeData.py". Here, we check
if the above script will work on valid data and then we will check if
every error stored in the json error file can be created.
"""

import pytest
import json
import zipfile
import csv
import shutil
from data_ingestion.extractCodeGradeData import *


@pytest.mark.django_db
class TestExportCodeGradeData:
    """TestExportCodeGradeData is a test suite for validating the functionality
    of the CodeGradeDataIngestion class. It ensures that the data extraction
    process works correctly under various scenarios, including valid and
    invalid data conditions.

    Attributes:
        test_directory (str): The directory used for storing test data.
        test_file (str): The base name of the test file used for testing.
        errorFileName (str): The name of the error file generated during tests.

    Methods:
        setup():
            A pytest fixture that sets up the test environment before each test
            and tears it down afterward. It creates necessary test files and directories.

        createSubmissions(zipData):
            Creates directories and placeholder files for student submissions.

        createJSON(jsonData):
            Creates a .cg-info.json file with the provided JSON data.

        createZIP(fileName):
            Creates a ZIP archive of the test directory and moves it to the test directory.

        createCSV(csvData, fileName):
            Creates a CSV file with the provided data.

        runAndProduceError():
            Executes the data extraction process and verifies that an error file is
            generated. Returns the error message from the error file.

        test_valid_data():
            Verifies that the data extraction process completes successfully when
            all student submission data is valid.

        test_duplicate_zip_files_found():
            Checks if the process correctly identifies duplicate ZIP files and
            produces an appropriate error.

        test_missing_cg_json_file():
            Ensures that an error is raised when the .cg-info.json file is missing
            from the ZIP directory.

        test_invalid_csv_file_name():
            Validates that an error is raised when the metadata CSV file name does
            not match the ZIP directory name.

        test_non_matching_student_submission_id():
            Checks if an error is raised when a student's submission ID does not
            match the expected ID in the submission folder.

        test_no_student_metadata():
            Ensures that an error is raised when no metadata entry exists for a
            student in the metadata CSV file.

        test_multiple_student_metadata():
            Verifies that an error is raised when multiple metadata entries exist
            for a single student in the metadata CSV file.

        test_student_name_not_matching_user_id():
            Checks if an error is raised when a student's user ID does not match
            their name in the metadata file.

        test_student_missing_submission_in_zip():
            Ensures that an error is raised when a student's submission is missing
            from the ZIP directory.
    """

    test_directory = "codegrade_data_test_directory"
    test_file = "CS 135 1001 - 2024 Fall - Assignment 0"
    errorFileName = "codegrade_data_errors.json"

    # Fixture to set up/teardown tests for this file
    @pytest.fixture(autouse=True)
    def setup(self):
        """Sets up the test environment for testing the CodeGradeDataIngestion
        class.

        This method performs the following steps:
        1. Creates a test directory if it does not already exist.
        2. Initializes an instance of the CodeGradeDataIngestion class with the test directory.
        3. Creates mock student submission data for testing purposes.
        4. Generates a JSON file containing submission and user IDs.
        5. Creates a ZIP file containing the test submissions.
        6. Generates a dummy CodeGrade metadata CSV file with previous submissions.
        7. Cleans up the test environment after the test is executed by removing the test directory
           and any error files created during the test.

        Note:
            - The test data includes three student submissions with associated metadata.
            - The teardown process ensures no residual files or directories remain after the test.
        """
        if not os.path.isdir(self.test_directory):
            os.mkdir(self.test_directory)

        self.ingest = CodeGradeDataIngestion(self.test_directory)

        # Set up zip directory with 3 student submissions for testing purposes
        test_data = ["0 - Mary Smith", "23 - James Johnson", "34 - John Jones"]
        self.createSubmissions(test_data)

        test_json = {
            "submission_ids": {
                "0 - Mary Smith": 0,
                "23 - James Johnson": 23,
                "34 - John Jones": 34,
            },
            "user_ids": {
                "0 - Mary Smith": 100000,
                "23 - James Johnson": 100001,
                "34 - John Jones": 100003,
            },
        }
        self.createJSON(test_json)
        self.createZIP(self.test_file)

        # Create CodeGrade metadata csv file with previous submissions
        dummy_csv_data = [
            ["Id", "Username", "Name", "Grade"],
            ["100000", "smithm", "Mary Smith", "79.1"],
            ["100001", "johnsj", "James Johnson", "81.7"],
            ["100003", "jonesj", "John Jones", "63.2"],
        ]
        self.createCSV(dummy_csv_data, self.test_file)

        yield

        # Teardown
        shutil.rmtree(self.test_directory)
        if self.errorFileName in os.listdir():
            os.remove(self.errorFileName)

    # The following 4 methods are used for custom test file creation
    # if a particular unit test needs to set up a file in a main way

    def createSubmissions(self, zipData):
        """Creates directories and files for submissions based on the provided
        zip data.

        Args:
            zipData (list): A list of strings where each string represents the name of a submission.

        Behavior:
            - For each entry in the zipData list, a directory is created inside the test directory.
            - Inside each created directory, an empty file named "main.cpp" is created.

        Note:
            - The method assumes that `self.test_directory` is a valid directory path.
            - If a directory or file already exists, this method may raise an exception.
        """
        for z in zipData:
            os.mkdir(f"{self.test_directory}/{z}")
            open(os.path.join(f"{self.test_directory}/{z}", "main.cpp"), "w")

    def createJSON(self, jsonData):
        """Creates a JSON file named '.cg-info.json' in the specified test
        directory and writes the provided JSON data into it.

        Args:
            jsonData (dict): The JSON data to be written to the file.

        Raises:
            FileNotFoundError: If the specified test directory does not exist.
            IOError: If there is an issue writing to the file.
        """
        with open(f"{self.test_directory}/.cg-info.json", "w") as jFile:
            json.dump(jsonData, jFile, indent=4)

    def createZIP(self, fileName):
        """Creates a ZIP archive of the specified directory, removes the
        original directory, recreates it, and moves the ZIP file into the newly
        created directory.

        Args:
            fileName (str): The name of the ZIP file to be created (without extension).

        Raises:
            OSError: If there is an issue with file or directory operations.
        """
        shutil.make_archive(
            f"{fileName}",
            "zip",
            f"{self.test_directory}",
        )
        shutil.rmtree(self.test_directory)
        os.mkdir(self.test_directory)
        shutil.move(
            f"{os.getcwd()}/{fileName}.zip",
            f"{os.getcwd()}/{self.test_directory}",
        )

    def createCSV(self, csvData, fileName):
        """Creates a CSV file with the provided data.

        Args:
            csvData (list of list): The data to be written to the CSV file, where each inner list represents a row.
            fileName (str): The name of the CSV file to be created (without the file extension).

        Writes:
            A CSV file in the specified test directory with the given data.
        """
        with open(f"{self.test_directory}/{fileName}.csv", "w") as file:
            csvFile = csv.writer(file)
            csvFile.writerows(csvData)

    # This is the same method as in the other script, I didn't want
    # to create a separate file to define it, so both methods will have
    # a copy of it
    def runAndProduceError(self):
        """Executes the `extractData` method and verifies if an error file is
        generated.

        This method checks for the presence of the error file in the current directory
        and reads its contents to extract the first error message. The error message
        is then returned for further validation or debugging.

        Returns:
            str: The first error message from the generated error file.

        Raises:
            AssertionError: If the expected error file is not found in the directory.
            FileNotFoundError: If the error file cannot be opened.
            KeyError: If the expected error structure in the JSON file is not found.
        """
        self.ingest.extractData()
        assert self.errorFileName in os.listdir()

        with open(self.errorFileName, "r") as errors:
            jsonFile = json.load(errors)
            msg = jsonFile["errors"][0]["_DataIngestionError__msg"]

        return msg

    # Test 1) This checks to make sure the export script executes correctly
    #         when all student submission data is valid
    def test_valid_data(self):
        """Test case for validating the extraction of data.

        This test ensures that the `extractData` method of the `ingest` object
        correctly processes data without generating an error file. It verifies
        that the `errorFileName` is not present in the current directory after
        the extraction process.

        Assertions:
            - The `errorFileName` should not exist in the list of files in the
              current working directory.
        """
        self.ingest.extractData()
        assert self.errorFileName not in os.listdir()

    # Test 2) This checks if there are 2 identical zip files and errors out
    def test_duplicate_zip_files_found(self):
        """Test case for verifying the behavior when duplicate .zip files are
        found.

        This test ensures that the `runAndProduceError` method correctly identifies
        and raises an error when a duplicate .zip file containing student submissions
        is present in the specified test directory.

        Steps:
        1. Create a .zip file in the test directory with the specified test file name.
        2. Run the `runAndProduceError` method.
        3. Assert that the returned error message matches the expected error message
           indicating the presence of a duplicate .zip file.

        Expected Behavior:
        - The method should return an error message specifying that a duplicate .zip
          file was found in the test directory.
        """
        with open(
            os.path.join(f"{self.test_directory}", f"{self.test_file}.zip"),
            "w",
        ):
            assert (
                self.runAndProduceError()
                == f"A duplicate .zip file was found containing student submission in {self.test_directory}"
            )

    # Test 3) This checks if the .json file is found in a given zip directory
    def test_missing_cg_json_file(self):
        """Test case for handling a missing .cg-info.json file during data
        ingestion.

        This test simulates a scenario where the .cg-info.json file is absent in the
        provided ZIP archive. It verifies that the system correctly identifies the
        missing file and produces the appropriate error message.

        Steps:
        1. Create a mock submission with a single student ("0 - Mary Smith").
        2. Generate a ZIP file named "CS 135 1001 - 2024 Fall - Assignment 1.zip"
           without including the .cg-info.json file.
        3. Run the data ingestion process and check if the error message
           "The .cg-info.json file is missing." is returned.

        Expected Outcome:
        The system should detect the absence of the .cg-info.json file and
        return the specified error message.
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 1.zip")
        assert self.runAndProduceError() == "The .cg-info.json file is missing."

    # Test 4) This test will see if the provided metadata csv file matches the zip
    #         directory name, and it will return an error if so
    def test_invalid_csv_file_name(self):
        """Test case for handling an invalid CSV file name during data
        ingestion.

        This test simulates a scenario where the expected CSV file for a specific
        assignment is not found in the designated test directory. It verifies that
        the system correctly identifies the missing file and produces the appropriate
        error message.

        Steps:
        1. Create a submission with a specific identifier ("0 - Mary Smith").
        2. Generate a JSON file mapping submission and user IDs.
        3. Create a ZIP file for the assignment ("CS 135 1001 - 2024 Fall - Assignment 1").
        4. Create a CSV file with an incorrect name ("CS 135 1001 - 2024 Fall - Assignment 2").
        5. Run the ingestion process and assert that the error message indicates
           the missing CSV file.

        Expected Behavior:
        The system should produce an error message stating that the expected CSV file
        ("CS 135 1001 - 2024 Fall - Assignment 1.csv") was not found in the test directory.
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 0},
                "user_ids": {"0 - Mary Smith": 100000},
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 1")
        self.createCSV(["error"], "CS 135 1001 - 2024 Fall - Assignment 2")
        assert (
            self.runAndProduceError()
            == f"CS 135 1001 - 2024 Fall - Assignment 1.csv was not found in {self.test_directory}."
        )

    # Test 5) This checks if a student's submission ID matches the submission ID found in
    #         their submission folder and if they don't match, then an error occurs
    def test_non_matching_student_submission_id(self):
        """Test case for handling non-matching student submission IDs.

        This test verifies that the system correctly identifies and reports an error
        when the submission ID for a student does not match the expected value.

        Steps:
        1. Create a submission for a student named "Mary Smith" with a specific ID.
        2. Generate a JSON file containing mismatched submission and user IDs for "Mary Smith".
        3. Create a ZIP file and a CSV file for the assignment "CS 135 1001 - 2024 Fall - Assignment 1".
        4. Run the process and check if the error message indicates the incorrect submission ID.

        Expected Outcome:
        The system should produce an error message stating:
        "The submission ID #0 for Mary Smith is not correct."
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 2},
                "user_ids": {"0 - Mary Smith": 100000},
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 1")
        self.createCSV(["error"], "CS 135 1001 - 2024 Fall - Assignment 1")
        assert (
            self.runAndProduceError()
            == "The submission ID #0 for Mary Smith is not correct."
        )

    # Test 6) This test will check if the codegrade metadata file contains no valid entry for a student
    def test_no_student_metadata(self):
        """Test case for handling the scenario where a student does not have
        associated metadata.

        This test simulates a situation where a student's metadata is missing by:
        - Creating a submission for a student named "Mary Smith".
        - Generating a JSON file with submission and user IDs for the student.
        - Creating a ZIP file for the assignment.
        - Creating a CSV file with assignment details but no metadata for the student.

        The test asserts that the system produces an error message indicating that
        the user ID (100000) does not have any metadata associated with it.
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 0},
                "user_ids": {"0 - Mary Smith": 100000},
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 2")
        self.createCSV(
            [["Id", "Username", "Name", "Grade"]],
            "CS 135 1001 - 2024 Fall - Assignment 2",
        )
        assert (
            self.runAndProduceError()
            == "User ID 100000 does not have any metadata associated with it."
        )

    # Test 7) This test will check if the codegrade metadata file contains multiple entries for a student
    def test_multiple_student_metadata(self):
        """Test case to verify the behavior of the system when a single user ID
        is associated with multiple metadata entries.

        Steps:
        1. Create a submission for a student named "Mary Smith".
        2. Generate a JSON file mapping the submission and user IDs for "Mary Smith".
        3. Create a ZIP file for the course "CS 135 1001 - 2024 Fall - Assignment 3".
        4. Create a CSV file containing multiple grade entries for the same user ID
           (100000) under the same course and assignment.
        5. Run the ingestion process and assert that the system produces an error
           indicating that the user ID has multiple metadata entries.

        Expected Outcome:
        The system should raise an error stating:
        "User ID 100000 has multiple metadata entries associated with it."
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 0},
                "user_ids": {"0 - Mary Smith": 100000},
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 3")
        self.createCSV(
            [
                ["Id", "Username", "Name", "Grade"],
                ["100000", "smithm", "Mary Smith", "79.1"],
                ["100000", "smithm", "Mary Smith", "78.1"],
            ],
            "CS 135 1001 - 2024 Fall - Assignment 3",
        )
        assert (
            self.runAndProduceError()
            == "User ID 100000 has multiple metadata entries associated with it."
        )

    # Test 8) This test will check if a student's user ID will match their name given in
    #         CodeGrade's metadata file and returns an error if they don't match
    def test_student_name_not_matching_user_id(self):
        """Test case to verify that an error is raised when the student name in
        the metadata file does not match the name associated with the user ID
        in the CSV file.

        Steps:
        1. Create a submission with a specific identifier and student name.
        2. Generate a JSON metadata file mapping the submission identifier to a
           user ID.
        3. Create a ZIP file representing the assignment submission.
        4. Generate a CSV file containing user details, including a mismatched
           student name for the given user ID.
        5. Run the process and assert that the error message indicates the mismatch
           between the user ID and the student name in the metadata file.

        Expected Outcome:
        The process should produce an error message stating that the user ID does
        not match the given name in the metadata file.
        """
        self.createSubmissions(["0 - Mary Smith"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 0},
                "user_ids": {"0 - Mary Smith": 100000},
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 4")
        self.createCSV(
            [
                ["Id", "Username", "Name", "Grade"],
                ["100000", "smithm", "Mary Jane", "79.1"],
            ],
            "CS 135 1001 - 2024 Fall - Assignment 4",
        )
        assert (
            self.runAndProduceError()
            == "User ID 100000 does not match the given name in the metadata file."
        )

    # Test 9) This test will check if a student's submission is missing in the zip
    #         directory and will return an error
    def test_student_missing_submission_in_zip(self):
        """Test case for verifying behavior when a student's submission is
        missing in the zip file.

        This test simulates a scenario where the submission for a student (Mary Smith) is not
        present in the zip directory, even though their information is included in the JSON
        and CSV files. The test ensures that the system correctly identifies and reports the
        missing submission.

        Steps:
        1. Create submissions for a specific student ("23 - Paul Jones").
        2. Generate a JSON file containing submission and user IDs for two students
           ("0 - Mary Smith" and "23 - Paul Jones").
        3. Create a zip file named "CS 135 1001 - 2024 Fall - Assignment 5".
        4. Generate a CSV file with grade information for both students.
        5. Run the process and assert that the error message indicates the missing submission
           for "Mary Smith".

        Expected Outcome:
        The system should produce an error message stating that the submission for
        "Mary Smith" is missing in the zip directory.
        """
        self.createSubmissions(["23 - Paul Jones"])
        self.createJSON(
            {
                "submission_ids": {"0 - Mary Smith": 0, "23 - Paul Jones": 23},
                "user_ids": {
                    "0 - Mary Smith": 100000,
                    "23 - Paul Jones": 100001,
                },
            }
        )
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 5")
        self.createCSV(
            [
                ["Id", "Username", "Name", "Grade"],
                ["100000", "smithm", "Mary Jane", "79.1"],
                ["100001", "jonesj", "Paul Jones", "89.3"],
            ],
            "CS 135 1001 - 2024 Fall - Assignment 5",
        )
        assert (
            self.runAndProduceError()
            == "Submission for Mary Smith is missing in zip directory."
        )
