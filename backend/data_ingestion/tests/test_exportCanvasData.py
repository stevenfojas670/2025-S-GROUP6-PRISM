import pytest
from data_ingestion.extractCanvasData import *

class TestExportCanvasData:

    test_directory = "test_directory"
    fileName = f"{test_directory}/2025-03-25T0637_Grades-CS_135_1000_-_2024_Sumr.csv"
    errorFileName = "canvas_data_errors.json"
    ingest = CanvasDataIngestion(test_directory)

    # Fixture to set up/teardown tests for this file
    @pytest.fixture
    def setup(self,request):
        if not os.path.isdir(self.test_directory):
            os.mkdir(self.test_directory)

        file = open(self.fileName,"w")
        file.write("Student,ID,SIS User ID,SIS Login ID,Integration ID,Section\n")
        file.write('"Student, Test",0000,studet,studet,5000000000,2245-CS-135-SEC1000-50000')
        file.close()

        def cleanup():
            for f in os.listdir(self.test_directory):
                os.remove(f"{self.test_directory}/{f}")
            os.removedirs(self.test_directory)
            if self.errorFileName in os.listdir():
                os.remove(self.errorFileName)

        request.addfinalizer(cleanup)

    # Test 1) This checks to make sure a valid student entry in the export
    #         Canvas gradebook file passes all error checks
    def test_valid_student_data(self,setup):
        self.ingest.extractData()
        assert(self.errorFileName not in os.listdir())

    # Test 2) This checks if a non-CSV file is inside the gradebook directory
    #         and should return an error.
    def test_invalid_file_in_gradebook_directory(self,setup):
        file = open(f"{self.test_directory}/bad_file.txt","w")
        self.ingest.extractData()
        assert(self.errorFileName in os.listdir())

    # Test 3) Here, we are checking if a student's user ID doesn't match
    #         their login ID, and we will return an error
    def test_non_matching_user_login_ids(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student2, Test",0000,stude,studet,5000000000,2245-CS-135-SEC1000-50000')
        self.ingest.extractData()
        assert(self.errorFileName in os.listdir())

    # Test 4) This test generates an error when a student's Canvas meta ID does
    #         not match the Canvas meta ID of the first student in the file
    def test_non_matching_canvaa_ids(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student3, Test",0000,studet,studet,5000000000,2245-CS-135-SEC1000-50003')
        self.ingest.extractData()
        assert (self.errorFileName in os.listdir())

    # Test 5) This test will check if the semester number specified in the Canvas
    #         meta ID matches the semester in the gradebook file name and return an error
    def test_non_matching_semester_ids(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student4, Test",0000,studet,studet,5000000000,2248-CS-135-SEC1000-50000')
        self.ingest.extractData()
        assert (self.errorFileName in os.listdir())

    # Test 6) This test will check if the course name in the Canvas meta ID matches
    #         the course name found in the gradebook file
    def test_non_matching_course_names(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student5, Test",0000,studet,studet,5000000000,2245-CS-202-SEC1000-50000')
        self.ingest.extractData()
        assert (self.errorFileName in os.listdir())

    # Test 7) This checks if a student's section is different from the section
    #         specified in the gradebook file name and returns an error
    def test_non_matching_section_ids(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student5, Test",0000,studet,studet,5000000000,2245-CS-135-SEC1001-50000')
        self.ingest.extractData()
        assert (self.errorFileName in os.listdir())

    # Test 8) This makes sure that the Canvas Meta ID contains a valid semester ID (first number
    #         ends in 2, 5, or 8) and returns an error if the semester can not be determined
    def test_invalid_semester_id(self,setup):
        with open(self.fileName,"a") as file:
            file.write('"Student5, Test",0000,studet,studet,5000000000,2249-CS-135-SEC1001-50000')
        self.ingest.extractData()
        assert (self.errorFileName in os.listdir())
