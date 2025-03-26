import pytest
import json
import zipfile
import csv
import shutil
from data_ingestion.extractCodeGradeData import *

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
                     "34 - John Jones": 34
                },
                "user_ids": {
                    "0 - Mary Smith": 100000,
                    "23 - James Johnson": 100001,
                    "34 - John Jones": 100003,
                }
        }
        self.createJSON(test_json)
        self.createZIP(self.test_file)

        # Create CodeGrade metadata csv file with previous submissions
        dummy_csv_data = [
            ['Id', 'Username', 'Name', 'Grade'],
            ['100000','smithm','Mary Smith','79.1'],
            ['100001','johnsj','James Johnson','81.7'],
            ['100003', 'jonesj', 'John Jones', '63.2']
        ]
        self.createCSV(dummy_csv_data,self.test_file)

        yield

        # Teardown
        shutil.rmtree(self.test_directory)
        if self.errorFileName in os.listdir():
            os.remove(self.errorFileName)

    def createSubmissions(self, zipData):
        for z in zipData:
            os.mkdir(f"{self.test_directory}/{z}")
            open(os.path.join(f"{self.test_directory}/{z}", 'main.cpp'), 'w')

    def createJSON(self, jsonData):
        with open(f"{self.test_directory}/.cg-info.json", "w") as jFile:
            json.dump(jsonData, jFile, indent=4)

    def createZIP(self,fileName):
        shutil.make_archive(f"{fileName}", "zip", f"{self.test_directory}", )
        shutil.rmtree(self.test_directory)
        os.mkdir(self.test_directory)
        shutil.move(f"{os.getcwd()}/{fileName}.zip", f"{os.getcwd()}/{self.test_directory}")

    def createCSV(self, csvData,fileName):
        with open(f"{self.test_directory}/{fileName}.csv", "w") as file:
            csvFile = csv.writer(file)
            csvFile.writerows(csvData)

    # This is the main method that will run when we are trying
    # to see if a particular error occurs
    def runAndProduceError(self):
        self.ingest.extractData()
        assert(self.errorFileName in os.listdir())

        with open(self.errorFileName,'r') as errors:
            jsonFile = json.load(errors)
            msg = jsonFile['errors'][0]['_DataIngestionError__msg']

        return msg


    # Test 1) This checks to make sure the export script executes correctly
    #         when all student submission data is valid
    def test_valid_data(self):
        self.ingest.extractData()
        assert (self.errorFileName not in os.listdir())

    # Test 2) This checks if there are 2 identical zip files and errors out
    def test_duplicate_zip_files_found(self):
        with open(os.path.join(f"{self.test_directory}", f'{self.test_file}.zip'), 'w'):
            assert(self.runAndProduceError() == f"A duplicate .zip file was found containing student submission in {self.test_directory}")

    def test_missing_cg_json_file(self):
        self.createSubmissions(["0 - Mary Smith"])
        self.createZIP('CS 135 1001 - 2024 Fall - Assignment 1.zip')
        assert(self.runAndProduceError() == "The .cg-info.json file is missing.")
