"""Created by Daniel Levy, 3/26/2025.

This is a unit test script for "extractCanvasData.py". This script checks if
the above script will work on valid data first and then it will check if all
errors in the json file can be generated correctly.
"""

import pytest
import json
import csv
from data_ingestion.extractCanvasData import *


# marking the class so Django allows it to touch the databsae and interact with it
@pytest.mark.django_db
class TestExportCanvasData:
    """TestExportCanvasData is a test suite for validating the functionality of
    the CanvasDataIngestion class. It ensures that the data extraction process
    from Canvas gradebook files works as expected and handles various error
    scenarios appropriately.

    Attributes:
        test_directory (str): Directory used for storing test files.
        fileName (str): Path to the test CSV file used in the tests.
        errorFileName (str): Name of the JSON file where errors are logged.

    Methods:
        setup():
            Fixture to set up the test environment by creating necessary directories and files,
            and tearing them down after the tests are executed.

        runAndProduceError():
            Executes the data extraction process and verifies that an error file is generated.
            Returns the error message from the error file.

        test_valid_student_data():
            Verifies that a valid student entry in the Canvas gradebook file passes all error checks.

        test_invalid_file_in_gradebook_directory():
            Checks if a non-CSV file in the gradebook directory triggers an appropriate error.

        test_non_matching_user_login_ids():
            Ensures that an error is raised when a student's user ID does not match their login ID.

        test_non_matching_semester_ids():
            Validates that an error is raised when the semester in the Canvas meta ID does not match
            the semester in the gradebook file name.

        test_non_matching_course_names():
            Ensures that an error is raised when the course name in the Canvas meta ID does not match
            the course name in the gradebook file.

        test_non_matching_section_ids():
            Verifies that an error is raised when a student's section does not match the section
            specified in the gradebook file name.

        test_non_matching_canvas_ids():
            Checks if an error is raised when a student's Canvas meta ID does not match the Canvas
            meta ID of the first student in the file.

        test_invalid_semester_id():
            Ensures that an error is raised when the Canvas meta ID contains an invalid semester ID.
    """

    test_directory = "canvas_data_test_directory"
    fileName = f"{test_directory}/2025-03-25T0637_Grades-CS_135_1000_-_2024_Sumr.csv"
    errorFileName = "canvas_data_errors.json"

    # Fixture to set up/teardown tests for this file
    @pytest.fixture(autouse=True)
    def setup(self):
        """Sets up the test environment for CanvasDataIngestion tests.

        - Creates a test directory if it does not exist.
        - Initializes a CanvasDataIngestion instance with the test directory.
        - Generates a dummy CSV file with sample data for testing.
        - Cleans up the test environment after the test is completed by:
            - Removing all files in the test directory.
            - Deleting the test directory.
            - Removing the error file if it exists in the current directory.
        """
        if not os.path.isdir(self.test_directory):
            os.mkdir(self.test_directory)

        self.ingest = CanvasDataIngestion(self.test_directory)

        dummy_data = [
            [
                "Student",
                "ID",
                "SIS User ID",
                "SIS Login ID",
                "Integration ID",
                "Section",
            ],
            [
                "Student, Test",
                "0000",
                "studet",
                "studet",
                "5000000000",
                "2245-CS-135-SEC1000-50000",
            ],
        ]

        with open(self.fileName, "w") as file:
            csvFile = csv.writer(file)
            csvFile.writerows(dummy_data)

        yield

        for f in os.listdir(self.test_directory):
            os.remove(f"{self.test_directory}/{f}")
        os.rmdir(self.test_directory)
        if self.errorFileName in os.listdir():
            os.remove(self.errorFileName)

    # This is the main method that will run when we are trying
    # to see if a particular error occurs
    def runAndProduceError(self):
        """Executes the data extraction process and verifies the presence of an
        error file.

        This method runs the `extractData` function from the `ingest` object, checks if the
        expected error file is present in the current directory, and reads the first error
        message from the JSON content of the error file.

        Returns:
            str: The error message from the first error in the error file.

        Raises:
            AssertionError: If the expected error file is not found in the current directory.
            FileNotFoundError: If the error file cannot be opened.
            json.JSONDecodeError: If the error file content is not valid JSON.
            KeyError: If the expected keys are not found in the JSON structure.
        """
        self.ingest.extractData()
        assert self.errorFileName in os.listdir()

        with open(self.errorFileName, "r") as errors:
            jsonFile = json.load(errors)
            msg = jsonFile["errors"][0]["_DataIngestionError__msg"]

        return msg

    # Test 1) This checks to make sure a valid student entry in the export
    #         Canvas gradebook file passes all error checks
    def test_valid_student_data(self):
        """Test case for validating the extraction of student data.

        This test ensures that the `extractData` method correctly processes
        student data without generating an error file. It asserts that the
        error file, identified by `self.errorFileName`, is not present in
        the current directory after the data extraction process.
        """
        self.ingest.extractData()
        assert self.errorFileName not in os.listdir()

    # Test 2) This checks if a non-CSV file is inside the gradebook directory
    #         and should return an error.
    def test_invalid_file_in_gradebook_directory(self):
        """Test case to verify the behavior of the system when an invalid file
        is present in the gradebook directory. Specifically, it ensures that
        the system correctly identifies and raises an error for a non-CSV file.

        Steps:
        1. Create a non-CSV file named 'bad_file.txt' in the test directory.
        2. Run the method `runAndProduceError` to simulate the error-checking process.
        3. Assert that the error message matches the expected output:
           "The file 'bad_file.txt' is not a valid .csv file."

        This test ensures the robustness of the file validation mechanism.
        """
        file = open(f"{self.test_directory}/bad_file.txt", "w")
        assert (
            self.runAndProduceError()
            == "The file 'bad_file.txt' is not a valid .csv file."
        )

    # Test 3) Here, we are checking if a student's user ID doesn't match
    #         their login ID, and we will return an error
    def test_non_matching_user_login_ids(self):
        """Test case for verifying behavior when user login IDs do not match.

        This test writes a row of test data to a CSV file, where the User ID
        and Login ID for a student do not match. It then asserts that the
        `runAndProduceError` method produces the expected error message
        indicating the mismatch.

        Test Data:
        - User: "Test Student3"
        - User ID: "stude"
        - Login ID: "studet"

        Expected Behavior:
        - The method `runAndProduceError` should return the error message:
          "The User ID for Test Student3 does not match the Login ID"
        """
        with open(self.fileName, "a") as file:
            test_data = [
                [
                    "Student3, Test",
                    "0000",
                    "stude",
                    "studet",
                    "5000000000",
                    "2245-CS-135-SEC1000-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)

        assert (
            self.runAndProduceError()
            == "The User ID for Test Student3 does not match the Login ID"
        )

    # Test 4) This test will check if the semester number specified in the Canvas
    #         meta ID matches the semester in the gradebook file name and return an error
    def test_non_matching_semester_ids(self):
        """Test case for verifying behavior when semester IDs do not match.

        This test writes test data to a file and checks if the system correctly
        identifies and raises an error when the semester ID for a student does not
        match the expected Canvas semester.

        Steps:
        1. Append test data containing a mismatched semester ID to the file.
        2. Run the method `runAndProduceError` to process the data.
        3. Assert that the returned error message matches the expected error string.

        Expected Behavior:
        - The system should raise an error indicating that the semester for the
          specified student does not match the Canvas semester.
        """
        with open(self.fileName, "a") as file:
            test_data = [
                [
                    "Student4, Test",
                    "0000",
                    "studet",
                    "studet",
                    "5000000000",
                    "2248-CS-135-SEC1000-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)

        assert (
            self.runAndProduceError()
            == "The semester for Test Student4 does not match the Canvas semester."
        )

    # Test 5) This test will check if the course name in the Canvas meta ID matches
    #         the course name found in the gradebook file
    def test_non_matching_course_names(self):
        """Test case for verifying behavior when course names do not match.

        This test writes a sample row of data with a mismatched course name to a file
        and asserts that the `runAndProduceError` method returns the expected error
        message indicating the mismatch.

        Steps:
        1. Open the file in append mode and write test data with a mismatched course name.
        2. Use the `runAndProduceError` method to process the data.
        3. Assert that the returned error message matches the expected error message.

        Expected Outcome:
        The method should return an error message stating that the course name for the
        specified student does not match the Canvas course name.
        """
        with open(self.fileName, "a") as file:
            test_data = [
                [
                    "Student5, Test",
                    "0000",
                    "studet",
                    "studet",
                    "5000000000",
                    "2245-CS-202-SEC1000-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)
        assert (
            self.runAndProduceError()
            == "The course name for Test Student5 does not match the Canvas course name."
        )

    # Test 6) This checks if a student's section is different from the section
    #         specified in the gradebook file name and returns an error
    def test_non_matching_section_ids(self):
        """Test case for verifying behavior when section IDs do not match.

        This test writes a row of test data to a CSV file with a mismatched section ID
        and asserts that the appropriate error message is produced when the data is processed.

        Test Data:
            - Name: "Student6, Test"
            - ID: "0000"
            - Role: "studet"
            - Login: "studet"
            - SIS ID: "5000000000"
            - Section: "2245-CS-135-SEC1001-50000"

        Expected Behavior:
            The method `runAndProduceError` should return the error message:
            "The section number for Test Student6 does not match the Canvas section."
        """
        with open(self.fileName, "a") as file:
            test_data = [
                [
                    "Student6, Test",
                    "0000",
                    "studet",
                    "studet",
                    "5000000000",
                    "2245-CS-135-SEC1001-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)
        assert (
            self.runAndProduceError()
            == "The section number for Test Student6 does not match the Canvas section."
        )

    # Test 7) This test generates an error when a student's Canvas meta ID does
    #         not match the Canvas meta ID of the first student in the file
    def test_non_matching_canvas_ids(self):
        """Test case to verify behavior when Canvas metadata IDs do not match.

        This test writes a row of test data with a non-matching Canvas metadata ID
        to a file and asserts that the `runAndProduceError` method produces the
        expected error message indicating the mismatch.

        Steps:
        1. Open the specified file in append mode and write test data containing
           a non-matching Canvas metadata ID.
        2. Use the `runAndProduceError` method to check for the error message.
        3. Assert that the error message matches the expected output.

        Expected Outcome:
        The method `runAndProduceError` should return the error message:
        "The Canvas metadata ID does not match for Test Student7."
        """
        with open(self.fileName, "a", newline="") as file:
            test_data = [
                [
                    "Student7, Test",
                    "0000",
                    "studet",
                    "studet",
                    "5000000000",
                    "3245-CS-135-SEC1000-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)

        assert (
            self.runAndProduceError()
            == "The Canvas metadata ID does not match for Test Student7."
        )

    # Test 8) This makes sure that the Canvas Meta ID contains a valid semester ID (first number
    #         ends in 2, 5, or 8) and returns an error if the semester can not be determined
    def test_invalid_semester_id(self):
        """Test case for validating the behavior of the system when an invalid
        semester ID is provided.

        This test writes a sample row of test data with an invalid semester ID to a CSV file
        and verifies that the system produces the expected error message.

        Steps:
        1. Open the specified file in append mode and write test data containing an invalid semester ID.
        2. Use the `runAndProduceError` method to process the data and capture the error message.
        3. Assert that the error message matches the expected output: "The semester is invalid."

        Expected Outcome:
        The system should correctly identify the invalid semester ID and return the appropriate error message.
        """
        with open(self.fileName, "a") as file:
            test_data = [
                [
                    "Student8, Test",
                    "0000",
                    "studet",
                    "studet",
                    "5000000000",
                    "2249-CS-135-SEC1000-50000",
                ]
            ]
            csvFile = csv.writer(file)
            csvFile.writerows(test_data)
        assert self.runAndProduceError() == "The semester is invalid."
