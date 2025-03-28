"""
Created by Daniel Levy, 3/26/2025

This is a unit test script for "extractCodeGradeData.py".
Here, we check if the above script will work on valid
data and then we will check if every error stored in the
json error file can be created.
"""

import pytest
import json
import zipfile
import csv
import shutil
from data_ingestion.extractCodeGradeData import *


@pytest.mark.django_db
class TestExportCodeGradeData:

    test_directory = "codegrade_data_test_directory"
    test_file = "CS 135 1001 - 2024 Fall - Assignment 0"
    errorFileName = "codegrade_data_errors.json"

    # Fixture to set up/teardown tests for this file
    @pytest.fixture(autouse=True)
    def setup(self):
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
        for z in zipData:
            os.mkdir(f"{self.test_directory}/{z}")
            open(os.path.join(f"{self.test_directory}/{z}", "main.cpp"), "w")

    def createJSON(self, jsonData):
        with open(f"{self.test_directory}/.cg-info.json", "w") as jFile:
            json.dump(jsonData, jFile, indent=4)

    def createZIP(self, fileName):
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
        with open(f"{self.test_directory}/{fileName}.csv", "w") as file:
            csvFile = csv.writer(file)
            csvFile.writerows(csvData)

    # This is the same method as in the other script, I didn't want
    # to create a separate file to define it, so both methods will have
    # a copy of it
    def runAndProduceError(self):
        self.ingest.extractData()
        assert self.errorFileName in os.listdir()

        with open(self.errorFileName, "r") as errors:
            jsonFile = json.load(errors)
            msg = jsonFile["errors"][0]["_DataIngestionError__msg"]

        return msg

    # Test 1) This checks to make sure the export script executes correctly
    #         when all student submission data is valid
    def test_valid_data(self):
        self.ingest.extractData()
        assert self.errorFileName not in os.listdir()

    # Test 2) This checks if there are 2 identical zip files and errors out
    def test_duplicate_zip_files_found(self):
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
        self.createSubmissions(["0 - Mary Smith"])
        self.createZIP("CS 135 1001 - 2024 Fall - Assignment 1.zip")
        assert (
            self.runAndProduceError() == "The .cg-info.json file is missing."
        )

    # Test 4) This test will see if the provided metadata csv file matches the zip
    #         directory name, and it will return an error if so
    def test_invalid_csv_file_name(self):
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
