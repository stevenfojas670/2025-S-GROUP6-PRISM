import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import builtins
from data_ingestion.api_data import API_Data


class TestAPIData(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.api = API_Data(self.mock_client)

    @patch("os.makedirs")
    def test_mkdir_success(self, mock_makedirs):
        mock_makedirs.return_value = None
        result = self.api.mkdir("some/dir")
        self.assertTrue(result)

    @patch("os.makedirs", side_effect=Exception("Error"))
    def test_mkdir_failure(self, mock_makedirs):
        result = self.api.mkdir("some/dir")
        self.assertFalse(result)

    def test_get_course_name_set(self):
        mock_course = MagicMock()
        mock_course.name = "Test Course"
        with patch("data_ingestion.api_data.select_from_list", return_value=mock_course):
            self.api.get_course(self.mock_client)
            self.assertEqual(self.api.course_name, "Test Course")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_get_json_file(self, mock_json_dump, mock_open_file):
        stud_dict = {"data": "test"}
        file_path = "./test_dir"
        with patch.object(self.api, "mkdir", return_value=True):
            self.api.get_json_file(stud_dict, file_path)
            mock_open_file.assert_called_once_with(os.path.join(file_path, ".cg-info.json"), "w")
            mock_json_dump.assert_called_once()

    @patch("os.path.exists", return_value=True)
    @patch("shutil.make_archive")
    def test_make_zip_archive_success(self, mock_make_archive, mock_exists):
        self.api.create_folder_path = "./test_data"
        self.api.make_zip_archive("testzip", "some_path")
        mock_make_archive.assert_called_once()

    def test_get_grade(self):
        grade = self.api.get_grade(100, 85)
        self.assertEqual(grade, 85.0)

    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    def test_extract_csv_no_submissions(self, mock_writer, mock_open_file):
        assignment = MagicMock()
        assignment.name = "Assignment 1"
        self.api.get_output_dir = MagicMock(return_value="dummy.csv")
        self.api.client.assignment.get_all_submissions.return_value = []

        self.api.extract_csv([assignment])
        self.api.client.assignment.get_all_submissions.assert_called()


if __name__ == "__main__":
    unittest.main()