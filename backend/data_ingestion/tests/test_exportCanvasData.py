import pytest
import os
from data_ingestion.extractCanvasData import *

class TestExportCanvasData:

    test_directory = "test_directory"
    errorFileName = "canvas_data_errors.json"
    ingest = CanvasDataIngestion(test_directory)

    @pytest.fixture
    def setup(self,request):
        if not os.path.isdir(self.test_directory):
            os.mkdir(self.test_directory)

        file = open(f"{self.test_directory}/2025-03-25T0637_Grades-CS_135_1000_-_2024_Sumr.csv","w")
        file.write("Student,ID,SIS User ID,SIS Login ID,Integration ID,Section\n")
        file.write('"Student, Test",0000,studet,studet,5000000000,2245-CS-135-SEC1000-50000')

        def cleanup():
            for f in os.listdir(self.test_directory):
                os.remove(f"{self.test_directory}/{f}")
            os.removedirs(self.test_directory)

        request.addfinalizer(cleanup)

    # Test 1) This checks to make sure a valid student entry in the export
    #         Canvas gradebook file passes all error checks
    def test_valid_student_data(self,setup):
        self.ingest.extractData()
        assert(self.errorFileName not in os.listdir())
