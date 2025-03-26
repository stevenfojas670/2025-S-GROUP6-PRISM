import os
import tempfile
import shutil
import unittest
import zipfile
import json
import pandas as pd
from unittest.mock import patch, MagicMock

# Import the CodeGradeDataIngestion class from your module
from data_ingestion.extractCodeGradeData import CodeGradeDataIngestion

class TestCodeGradeDataIngestion(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to simulate the project directory
        self.temp_dir = tempfile.mkdtemp()
        # Create a subdirectory named "codegrade_data" (as expected by extractData)
        self.codegrade_data_dir = os.path.join(self.temp_dir, "codegrade_data")
        os.mkdir(self.codegrade_data_dir)
        # Save the current working directory and change to temp_dir so that "codegrade_data" is found.
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create a dummy ZIP file with the proper naming convention:
        # "CS101 Intro 001 - 2025_Spring - Assignment1.zip"
        self.zip_filename = "CS101 Intro 001 - 2025_Spring - Assignment1.zip"
        self.zip_filepath = os.path.join(self.codegrade_data_dir, self.zip_filename)

        # The submission file name is the ZIP filename without the ".zip"
        self.submission_filename = self.zip_filename.removesuffix(".zip")
        # The CSV file must match the submission filename with a .csv extension.
        self.csv_filename = f"{self.submission_filename}.csv"
        self.csv_filepath = os.path.join(self.codegrade_data_dir, self.csv_filename)

        # Create a dummy zip file that contains:
        # - A .cg-info.json file with dummy submission_ids and user_ids.
        # - A dummy file named "123 - John Doe" to simulate a student submission.
        with zipfile.ZipFile(self.zip_filepath, 'w') as zf:
            cg_info = {
                "submission_ids": {"123 - John Doe": 123},
                "user_ids": {"123 - John Doe": 456}
            }
            zf.writestr(".cg-info.json", json.dumps(cg_info))
            zf.writestr("123 - John Doe", "dummy submission content")

        # Create a dummy CSV file with the required columns: "Id", "Username", "Name"
        df = pd.DataFrame({
            "Id": [456],
            "Username": ["jdoe"],
            "Name": ["John Doe"]
        })
        df.to_csv(self.csv_filepath, index=False)

    def tearDown(self):
        # Restore the original working directory and remove the temporary directory
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
        # Clear any accumulated static errors
        CodeGradeDataIngestion.allErrors = []

    @patch('assignments.models.Student.objects.get_or_create', return_value=(MagicMock(), True))
    @patch('data_ingestion.extractCodeGradeData.DataIngestionError.createErrorJSON')
    def test_extract_data_success(self, mock_create_error_json, mock_get_or_create):
        # Instantiate the ingestion class with our simulated codegrade_data folder.
        ingestion = CodeGradeDataIngestion(self.codegrade_data_dir)
        # Run the extraction process.
        ingestion.extractData()
        # Assert that no errors were recorded.
        self.assertEqual(len(CodeGradeDataIngestion.allErrors), 0)
        # Ensure that the error reporting method was not called.
        mock_create_error_json.assert_not_called()

if __name__ == '__main__':
    unittest.main()