"""Created by Eli Rosales, 3/2/2025.

This script is part of the Data Ingestion phase of PRISM.
It automates the extraction of assignment data and student submissions from CodeGrade.
"""

import os
import io
import sys
import time
import json
import csv
import shutil
import zipfile
import datetime

import httpx
import codegrade
from codegrade.utils import select_from_list


class API_Data:
    """Handles CodeGrade API interactions and data extraction."""

    def __init__(self, client):
        """Initialize the API_Data instance with the authenticated CodeGrade client."""
        self.client = client
        self.course_name = ""
        self.course = self.get_course(client)
        self.assignments = self.get_assignments()
        self.create_folder_path = ""
        self.course_info = {}
        self.all_assignments = []
        self.graders = []
        self.rubric_grades = []
        self.rubrics = {}
        self.all_assignment_submissions = {}

    def handle_maybe(self, maybe):
        """Handle a 'maybe' object and extract its value."""
        return maybe.try_extract(lambda: SystemExit(1))

    def mkdir(self, dir_path):
        """Create a directory if it does not exist."""
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(str(e), file=sys.stderr)
            return False
        return True

    def get_course(self, client):
        """Retrieve a course from the client via user selection."""
        try:
            course = self.handle_maybe(
                select_from_list(
                    "Select a course",
                    client.course.get_all(),
                    lambda c: c.name,
                )
            )
        except Exception as e:
            return e
        self.course_name = course.name
        return course

    def get_assignments(self):
        """Retrieve the list of assignments associated with the selected course."""
        return self.course.assignments

    def get_course_info(self):
        """Return course information as a dictionary."""
        return {
            "Course-ID": self.course.id,
            "Name": self.course.name,
            "Created-Date": self.course.created_at,
        }

    def get_rubric_grades_dict(self, assignments):
        """Generate a dictionary containing rubric grades for submissions."""
        grade_dict = {}
        for assignment in assignments:
            submissions = self.get_all_submissions(assignment)
            for submission in submissions:
                sub_id_key = f"{submission.id} - {submission.user.name}"
                grade_dict[sub_id_key] = []
                self.get_rubric_value(
                    rubric=self.get_rubric_grade(submission.id),
                    grade_dict=grade_dict,
                    sub_id_key=sub_id_key,
                )
        return grade_dict

    def get_rubric_value(self, rubric, grade_dict, sub_id_key):
        """Extract rubric values and append them to the grade dictionary."""
        for index, obj in enumerate(rubric.selected):
            grade_dict[sub_id_key].append({
                "header": rubric.rubrics[index].header,
                "points_achieved": obj.achieved_points,
                "points_possible": obj.points,
                "multiplier": obj.multiplier,
            })

    def get_all_submissions(self, assignment):
        """Return all submissions for a given assignment."""
        try:
            return self.client.assignment.get_all_submissions(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_all_graders(self, assignment):
        """Return all graders for a given assignment."""
        try:
            return self.client.assignment.get_all_graders(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_rubric(self, assignment):
        """Return the rubric for a given assignment."""
        try:
            return self.client.assignment.get_rubric(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_desc(self, assignment):
        """Return the assignment description."""
        try:
            return self.client.assignment.get_description(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_time_frames(self, assignment):
        """Return the time frames for a given assignment."""
        try:
            return self.client.assignment.get_timeframes(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_feedback(self, assignment):
        """Return all feedback for a given assignment."""
        try:
            return self.client.assignment.get_all_feedback(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))

    def get_users(self, course):
        """Return all users enrolled in the given course."""
        try:
            return self.client.course.get_all_users(course_id=course.id)
        except Exception as e:
            print(str(e))

    def get_all_user_submissions(self, course, user_id):
        """Return all submissions by a specific user in a course."""
        try:
            return self.client.course.get_submissions_by_user(
                course_id=course.id, user_id=user_id
            )
        except Exception as e:
            print(str(e))

    def get_rubric_grade(self, submission_id):
        """Return the rubric grade for a submission."""
        try:
            return self.client.submission.get_rubric_result(
                submission_id=submission_id
            )
        except Exception:
            return None

    def get_json_file(self, stud_dict, file_path):
        """Generate and save a JSON file from the student dictionary."""
        file_output = os.path.join(file_path, ".cg-info.json")
        print('Making json file ".cg-info.json"')
        if not self.mkdir(file_path):
            return
        with open(file_output, "w") as file:
            json.dump(stud_dict, file)

    def download_submission(self, submission, output_dir, *, retries=5):
        """Download and extract a student's submission ZIP."""
        try:
            zipinfo = self.client.submission.get(
                submission_id=submission.id,
                type="zip",
            )
            zipdata = self.client.file.download(filename=zipinfo.name)
        except httpx.ReadError:
            if not retries:
                raise
            time.sleep(1)
            return self.download_submission(
                submission,
                output_dir,
                retries=retries - 1,
            )

        username = submission.user.name
        if submission.user.group:
            username = f"{submission.user.group.name} (Group)"

        student_output_dir = os.path.join(output_dir, username)
        if not self.mkdir(student_output_dir):
            return

        try:
            with zipfile.ZipFile(io.BytesIO(zipdata), "r") as zipf:
                for file in zipf.namelist():
                    filename = os.path.basename(file)
                    if not filename:
                        continue
                    with zipf.open(file) as source, open(
                        os.path.join(student_output_dir, filename), "wb"
                    ) as target:
                        shutil.copyfileobj(source, target)
        except zipfile.BadZipFile:
            print("Invalid zip file", file=sys.stderr)

    def get_output_dir(self, course_name, assignment):
        """Return the output directory path for the assignment."""
        self.create_folder_path = os.path.join(os.getcwd(), "cg_data")
        file_name = f"{course_name} - {assignment.name}"
        return os.path.join(self.create_folder_path, file_name)

    def get_sorted_dict(self, stud_dict):
        """Sort nested dictionaries for consistency."""
        stud_dict["submission_ids"] = sorted(stud_dict["submission_ids"].items())
        stud_dict["user_ids"] = sorted(stud_dict["user_ids"].items())
        for key1 in stud_dict:
            curr_dict = {}
            for key, value in stud_dict[key1]:
                curr_dict[key] = value
            stud_dict[key1] = curr_dict
        return stud_dict

    def make_zip_archive(self, zip_file_name, dir_path):
        """Create a ZIP archive from a directory."""
        if not os.path.exists(dir_path):
            print(
                f"Unable to create '{zip_file_name}.zip' because the folder was not found."
            )
            return
        dest_path = os.path.join(self.create_folder_path, zip_file_name)
        shutil.make_archive(dest_path, "zip", dir_path)
        print(f"SUCCESS! File '{zip_file_name}.zip' has been created!")

    def extract_all_assignments(self, assignments):
        """Extract submissions and metadata for all closed assignments."""
        print(f"Extracting all assignments from {self.course.name}:\n")
        for assignment in assignments:
            submissions = self.client.assignment.get_all_submissions(
                assignment_id=assignment.id, latest_only=True
            )

            now = datetime.datetime.now()
            lock_date = assignment.lock_date or assignment.deadline
            lock_date = datetime.datetime(
                lock_date.year, lock_date.month, lock_date.day,
                lock_date.hour, lock_date.minute, lock_date.second
            )

            after_lock_date = lock_date < now
            if submissions and after_lock_date:
                output_dir = self.get_output_dir(self.course.name, assignment)
                students = {"submission_ids": {}, "user_ids": {}}
                print(f"\nExtracting submission source code for {assignment.name}:")
                for submission in submissions:
                    sub_id = submission.id
                    key = f"{sub_id} - {submission.user.name}"
                    students["submission_ids"][key] = sub_id
                    students["user_ids"][key] = submission.user.id
                    print("Downloading", submission.user.name)
                    self.download_submission(submission, output_dir)

                students = self.get_sorted_dict(students)
                self.get_json_file(students, output_dir)
                print(f"{self.course.name} - {assignment.name} successfully completed.")
                print(f'\nMaking "{self.course.name} - {assignment.name}" into a zip file')
                self.make_zip_archive(f"{self.course.name} - {assignment.name}", output_dir)
            elif not after_lock_date:
                print(f"Lock date ({lock_date}) has not passed yet for {assignment.name}")
            else:
                print(f"No submissions for {assignment.name}")

    def get_grade(self, max_grade, grade_achieved):
        """Return normalized grade scaled to a 100-point scale."""
        if max_grade == 0:
            return 0
        return (grade_achieved / max_grade) * 100

    def extract_csv(self, assignments):
        """Generate CSV files with ID, username, name, and grade for each assignment."""
        print(f"\nExtracting .CSV files for class: '{self.course.name}'")
        for assignment in assignments:
            submissions = self.client.assignment.get_all_submissions(
                assignment_id=assignment.id, latest_only=True
            )

            now = datetime.datetime.now()
            lock_date = assignment.lock_date or assignment.deadline
            lock_date = datetime.datetime(
                lock_date.year, lock_date.month, lock_date.day,
                lock_date.hour, lock_date.minute, lock_date.second
            )

            after_lock_date = lock_date < now
            if submissions and after_lock_date:
                rows = ["Id", "Username", "Name", "Grade"]
                file_name = f"{self.get_output_dir(self.course.name, assignment)}.csv"

                with open(file_name, "w", newline="") as file_csv:
                    writer = csv.writer(file_csv)
                    writer.writerow(rows)
                    self.get_feedback(assignment)
                    for submission in submissions:
                        grade = self.get_grade(assignment.max_grade, submission.grade)
                        writer.writerow([
                            submission.user.id,
                            submission.user.username,
                            submission.user.name,
                            round(grade, 2),
                        ])
                print(f"SUCCESS! Created file '{file_name}'")
            elif not after_lock_date:
                print(f"Lock date ({lock_date}) has not passed yet for {assignment.name}")
            else:
                print(f"No submissions for {assignment.name}")

    def delete_created_folder(self):
        """Delete the directory created to store extracted files."""
        try:
            shutil.rmtree(self.create_folder_path)
            print(f"Directory '{self.create_folder_path}' and its contents deleted successfully.")
        except FileNotFoundError:
            print(f"Directory '{self.create_folder_path}' not found.")
        except PermissionError:
            print(f"You do not have permission to delete '{self.create_folder_path}'.")
        except OSError as e:
            print(f"Error deleting '{self.create_folder_path}': {e}")


def main():
    """Execute the full data ingestion pipeline from CodeGrade."""
    client = codegrade.login_from_cli()
    cg_data = API_Data(client)

    cg_data.extract_all_assignments(cg_data.assignments)
    cg_data.extract_csv(cg_data.assignments)
    cg_data.delete_created_folder()


if __name__ == "__main__":
    main()
