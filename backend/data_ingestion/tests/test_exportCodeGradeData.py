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
        for t in test_data:
            os.mkdir(f"{self.test_directory}/{t}")
            open(os.path.join(f"{self.test_directory}/{t}", 'main.cpp'), 'w')

        with zipfile.ZipFile(f"{self.test_file}.zip",'w') as zFile:
            for dir, subdirs, files in os.walk(self.test_directory):
                for f in files:
                    path = os.path.join(dir,f)
                    zFile.write(path)

        # Create CodeGrade metadata csv file with previous submissions
        dummy_csv_data = [
            ['Id', 'Username', 'Name', 'Grade'],
            ['100000','smithm','Mary Smith','79.1'],
            ['100001','johnsj','James Johnson','81.7'],
            ['100003', 'jonesj', 'John Jones', '63.2']
        ]

        with open(f"{self.test_file}.csv", "w") as file:
            csvFile = csv.writer(file)
            csvFile.writerows(dummy_csv_data)

        shutil.rmtree(self.test_directory)

        yield

        # Teardown
        os.remove(f"{self.test_file}.zip")
        os.remove(f"{self.test_file}.csv")
        if self.errorFileName in os.listdir():
            os.remove(self.errorFileName)

    # This is the main method that will run when we are trying
    # to see if a particular error occurs
    def runAndProduceError(self):
        self.ingest.extractData()
        assert(self.errorFileName in os.listdir())

        with open(self.errorFileName,'r') as errors:
            jsonFile = json.load(errors)
            msg = jsonFile['errors'][0]['_DataIngestionError__msg']

        return msg

    def test_valid_data(self):
        self.ingest.extractData()
        assert (self.errorFileName not in os.listdir())
