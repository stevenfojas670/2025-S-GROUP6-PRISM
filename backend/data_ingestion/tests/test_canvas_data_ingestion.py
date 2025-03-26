import os
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

from data_ingestion.canvas_data import CanvasDataIngestion

class TestCanvasDataIngestion(unittest.TestCase):

    @patch('data_ingestion.canvas_data.Semester.objects.get_or_create')
    @patch('data_ingestion.canvas_data.Class.objects.get_or_create')
    def test_extract_valid_data(self, mock_class_get_or_create, mock_semester_get_or_create):
        # Setup test directory and dummy CSV
        test_dir = 'test_canvas_data'
        os.makedirs(test_dir, exist_ok=True)
        test_csv_path = os.path.join(test_dir, "canvas-export-123-CS472_001-2025_Sprg.csv")

        df = pd.DataFrame({
            'Student': ['John Doe'],
            'SIS User ID': ['abc123'],
            'SIS Login ID': ['abc123'],
            'Section': ['20252-CS-472-001-01']
        })
        df.to_csv(test_csv_path, index=False)

        ingestion = CanvasDataIngestion(test_dir)
        ingestion.extractData()

        self.assertEqual(len(ingestion.errors), 0)

        # Cleanup
        os.remove(test_csv_path)
        os.rmdir(test_dir)

    def test_invalid_file_extension(self):
        test_dir = 'test_invalid_file'
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, "invalid.txt"), "w") as f:
            f.write("Not a CSV")

        ingestion = CanvasDataIngestion(test_dir)
        ingestion.extractData()

        self.assertGreater(len(ingestion.errors), 0)

        # Cleanup
        os.remove(os.path.join(test_dir, "invalid.txt"))
        os.rmdir(test_dir)

if __name__ == '__main__':
    unittest.main()