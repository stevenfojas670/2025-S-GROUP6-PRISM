"""Created by Eli Rosales, 3/2/2025.

This script is a part of the Data Ingestion phase of PRISM. This script will
automate the need for manual data extraction from codegrade. It will extract
the csv with
"""

import io
import os
import sys
import time
import zipfile
import codegrade
import httpx
import shutil
import json
import csv
from codegrade.utils import select_from_list
import datetime


class API_Data:
    """API_Data Class.

    This class provides functionality to interact with the CodeGrade API for extracting and processing
    course, assignment, and submission data. It includes methods for retrieving data, creating directories,
    downloading submissions, generating JSON and CSV files, and creating zip archives.

    Attributes:
        client (object): Authenticated CodeGrade client.
        course (object): Selected course object from CodeGrade.
        course_name (str): Name of the selected course.
        assignments (list): List of assignments in the selected course.
        create_folder_path (str): Path to the directory for storing generated files.
        course_info (dict): Dictionary containing course information.
        all_assignments (list): List of all assignments in the course.
        graders (list): List of graders for the course.
        rubric_grades (list): List of tuples containing rubric grades.
        rubrics (dict): Dictionary containing rubric details for assignments.
        all_assignment_submissions (dict): Dictionary containing all assignment submissions.

    Methods:
        __init__(client): Initializes the API_Data object with the authenticated client.
        handle_maybe(maybe): Handles exceptions and exits the program if necessary.
        mkdir(dir): Creates a directory if it does not exist.
        get_course(client): Retrieves and selects a course from the CodeGrade API.
        get_assignments(): Retrieves assignments for the selected course.
        get_course_info(): Retrieves and formats course information into a dictionary.
        get_rubric_grades_dict(assignments): Retrieves rubric grades for all submissions in assignments.
        get_rubric_value(rubric, grade_dict, sub_id_key): Parses rubric values into a dictionary.
        get_all_submissions(assignment): Retrieves all submissions for a given assignment.
        get_all_graders(assignment): Retrieves all graders for a given assignment.
        get_rubric(assignment): Retrieves the rubric for a given assignment.
        get_desc(assignment): Retrieves the description of a given assignment.
        get_time_frames(assignment): Retrieves the timeframes for a given assignment.
        get_feedback(assignment): Retrieves feedback for a given assignment.
        get_users(course): Retrieves all users in the selected course.
        get_all_user_submissions(course, user_id): Retrieves all submissions for a specific user in the course.
        get_rubric_grade(submission_id): Retrieves the rubric grade for a specific submission.
        get_json_file(stud_dict, file_path): Creates a JSON file with student data.
        download_submission(submission, output_dir, retries=5): Downloads a submission as a zip file.
        get_output_dir(course_name, assignment): Generates the output directory path for an assignment.
        get_sorted_dict(studDict): Sorts and formats a dictionary of student data.
        make_zip_archive(zip_file_name, dir_path): Creates a zip archive of a directory.
        extract_all_assignments(assignments): Extracts all assignments and creates zip files for submissions.
        get_grade(max_grade, grade_achieved): Calculates the grade percentage based on achieved and maximum grades.
        extract_csv(assignments): Extracts assignment data into a CSV file.
        delete_created_folder(): Deletes the created folder and its contents.
    """

    # variables
    """
    1. client                         (cg client)                                                             #CODEGRADE AUTHENTICATED CLIENT
    2. course                         (cg courseService)                                                      #STR
    3. course_name                    (str)                                                                   #STR
    4. all_assignments []             ([(assignment_id,assignemnt_name),(assignment_id,assignemnt_name)...])  #LIST OF TUPLES
    5. rubric {}                      ({"assignment_id":  {header1:[header_name,points],header2:'',...}})     #DIC
    6. all_assignment_submissions {}  ({"assignment_id":  [sub_id,sub_id...] })                               #DIC
    7. graders {}                     ([[grader_name,grader_username,grader_user_id],...])                    #LIST OF LISTS
    8. rubric_grades {}               ([("sub_id - user.name",points achieved)])                              #LIST OF TUPLES
    9. course_info                    ({'id':id,  'name':name,    'date':date})

    10. submisions
    11. assignments
    12. create folder path              path to the 'cg_data' directory(storing all files made by this script)
    """

    def __init__(self, client):
        """Initializes the class with the provided client and sets up various
        attributes for managing course and assignment data.

        Args:
            client: The client object used to interact with the API.

        Attributes:
            client: The client object passed during initialization.
            course_name (str): The name of the course, initialized as an empty string.
            course: The course data retrieved using the client.
            assignments: The assignment data retrieved using the client.
            create_folder_path (str): Path for creating folders, initialized as an empty string.
            course_info (dict): A dictionary to store course information in a human-readable format.
            all_assignments (list): A list to store all assignments, initialized as an empty list.
            graders (list): A list to store grader information, initialized as an empty list.
            rubric_grades (list): A list to store rubric grades, initialized as an empty list.
            rubrics (dict): A dictionary to store rubric data for assignments,
                            initialized as an empty dictionary with assignment IDs as keys.
            all_assignment_submissions (dict): A dictionary to store submissions for each assignment,
                                               initialized as an empty dictionary with assignment IDs as keys.
        """
        # main will handle the username and password
        # part(retrieve from frontend)
        # self.__username               = username (parameter)  #__private_var
        # self.__password               = password (parameter) #__prvate_var
        self.client = client
        self.course_name = ""
        self.course = self.get_course(client)
        self.assignments = self.get_assignments()
        self.create_folder_path = ""
        # To output in a human readable format
        self.course_info = {}
        self.all_assignments = self.graders = self.rubric_grades = []
        self.rubrics = {}  # {"assignment_id": {}, "assignment_id": {}}
        self.all_assignment_submissions = (
            {}
        )  # {"assignment_id": [], "assignment_id": []}

    # helper functions
    def handle_maybe(self, maybe):
        """Handles a "maybe" object by attempting to extract its value using a
        provided function.

        Args:
            maybe: An object that supports the `try_extract` method, which takes a callable
                   and attempts to extract a value or handle an error.

        Returns:
            The result of the `try_extract` method, which may vary depending on the implementation
            of the `maybe` object and the callable provided.

        Raises:
            SystemExit: If the extraction fails, the callable provided to `try_extract` will
                        raise a `SystemExit` with exit code 1.
        """
        return maybe.try_extract(lambda: SystemExit(1))

    def mkdir(self, dir):
        """Creates a directory if it does not already exist.

        Args:
            dir (str): The path of the directory to create.

        Returns:
            bool: True if the directory was successfully created or already exists,
                  False if an exception occurred during the creation process.

        Raises:
            Exception: Any exception that occurs during the directory creation
                       process is caught and printed to standard error.
        """
        try:
            os.makedirs(dir, exist_ok=True)
        except Exception as e:
            print(str(e), file=sys.stderr)
            return False
        else:
            return True

    def get_course(self, client):
        """Retrieves a course from the client by presenting a selection list to
        the user.

        Args:
            client: An object that provides access to course data through a `get_all` method.

        Returns:
            The selected course object if successful, or an exception object if an error occurs.

        Raises:
            Exception: Propagates any exception that occurs during the course selection process.

        Side Effects:
            Sets the `course_name` attribute of the instance to the name of the selected course.
        """
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
        else:
            self.course_name = course.name
            return course

    # Populate class vars and output data in a human readable format
    def get_assignments(self):
        """Retrieves the list of assignments associated with the course.

        Returns:
            list: A list of assignments for the course.
        """
        return self.course.assignments

    # TODO vvv finish these methods
    def get_course_info(self):
        """Retrieves information about a course and returns it as a dictionary.

        Returns:
            dict: A dictionary containing the following course information:
                - "Course-ID" (str): The unique identifier of the course.
                - "Name" (str): The name of the course.
                - "Created-Date" (datetime): The date and time when the course was created.
        """
        course_dict = {}
        course_dict["Course-ID"] = self.course.id
        course_dict["Name"] = self.course.name
        course_dict["Created-Date"] = self.course.created_at
        return course_dict

    def get_rubric_grades_dict(self, assignments):
        """Generates a dictionary containing rubric grades for student
        submissions.

        Args:
            assignments (list): A list of assignment objects for which rubric grades
                                need to be extracted.

        Returns:
            dict: A dictionary where each key is a string in the format
                  "submissionID - Stud_name", and the value is a list of dictionaries
                  containing the following keys:
                    - "header" (str): The header or description of the rubric item.
                    - "points_achieved" (float): The points achieved by the student
                                                 for the rubric item.
                    - "points_possible" (float): The maximum points possible for the
                                                  rubric item.
                    - "multiplier" (float): The multiplier applied to the rubric item.

        Notes:
            - The method retrieves all submissions for each assignment and processes
              their rubric grades.
            - The `get_rubric_value` method is used to populate the rubric grade
              details for each submission.
        """
        """{"submissionID - Stud_name":
                                    [{"header":          ''
                                     "points_achieved":  0
                                     "points_possible":  0
                                     "multiplier":       0 },
                                     {}]
        submissionID = Stud_name...
        }
        """
        grade_dict = {}  # dictionary to return
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

    # helper funciton:
    def get_rubric_value(self, rubric, grade_dict, sub_id_key):
        """Extracts and appends rubric data to the grade dictionary for a
        specific subject ID key.

        Args:
            rubric (object): An object containing rubric information, including selected items
                             and their corresponding details such as achieved points, possible points,
                             and multipliers.
            grade_dict (dict): A dictionary where the subject ID key maps to a list of rubric results.
            sub_id_key (str): The key representing the subject ID in the grade dictionary.

        Returns:
            None: The function modifies the grade_dict in place by appending parsed rubric data.
        """
        # return a dictionary parsed with the info.
        index = 0
        for obj in rubric.selected:
            result = {}
            result["header"] = f"{rubric.rubrics[index].header}"
            result["points_achieved"] = obj.achieved_points
            result["points_possible"] = obj.points
            result["multiplier"] = obj.multiplier
            grade_dict[sub_id_key].append(result)
            index = index + 1

    """
    def get_rubrics(self):
        return None
    def get_all_assignments(self):
        return None
    def get_all_graders(self):
        return None
    def get_all_assignment_subs(self):
        return None
    """

    # Getters from API:
    # ASSIGNMENT SERVICE TYPE
    def get_all_submissions(self, assignment):
        """Retrieves all submissions for a given assignment.

        Args:
            assignment (object): The assignment object containing the assignment ID.

        Returns:
            list: A list of submissions for the specified assignment if successful.
            None: If an exception occurs during the retrieval process.

        Raises:
            Exception: Logs the exception message if an error occurs while fetching submissions.
        """
        try:
            submissions = self.client.assignment.get_all_submissions(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))
        else:
            return submissions

    def get_all_graders(self, assignment):
        """Retrieves all graders for a given assignment.

        Args:
            assignment (object): The assignment object containing the assignment ID.

        Returns:
            list: A list of graders associated with the assignment if successful.
            None: If an exception occurs during the retrieval process.

        Raises:
            Exception: Logs the exception message if an error occurs while fetching graders.
        """
        try:
            graders = self.client.assignment.get_all_graders(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))
        else:
            return graders

    def get_rubric(self, assignment):
        """Retrieves the rubric for a given assignment using the client API.

        Args:
            assignment (object): The assignment object containing the assignment ID.

        Returns:
            object: The rubric associated with the assignment if retrieval is successful.
            None: If an exception occurs during the retrieval process.

        Raises:
            Exception: Prints the exception message if an error occurs while fetching the rubric.
        """
        try:
            rubric = self.client.assignment.get_rubric(assignment_id=assignment.id)
        except Exception as e:
            print(str(e))
        else:
            return rubric

    def get_desc(self, assignment):
        """Retrieves the description of a given assignment using the client
        API.

        Args:
            assignment (object): An object representing the assignment, which must have an `id` attribute.

        Returns:
            str: The description of the assignment if successfully retrieved.
            None: If an exception occurs during the retrieval process.

        Raises:
            Exception: Any exception raised during the API call is caught and printed.
        """
        try:
            desc = self.client.assignment.get_description(assignment_id=assignment.id)
        except Exception as e:
            print(str(e))
        else:
            return desc

    def get_time_frames(self, assignment):
        """Retrieves the time frames associated with a given assignment.

        Args:
            assignment (object): The assignment object containing the assignment ID.

        Returns:
            list: A list of time frames associated with the assignment if successful.
            None: If an exception occurs during the retrieval process.

        Raises:
            Exception: Prints the exception message if an error occurs.
        """
        try:
            times = self.client.assignment.get_timeframes(assignment_id=assignment.id)
        except Exception as e:
            print(str(e))
        else:
            return times

    def get_feedback(self, assignment):
        """Retrieves all feedback for a given assignment using the client API.

        Args:
            assignment (object): The assignment object containing the assignment ID.

        Returns:
            list: A list of feedback objects associated with the assignment,
                  or None if an exception occurs.

        Raises:
            Exception: Captures and prints any exception that occurs during the API call.
        """
        try:
            feedback = self.client.assignment.get_all_feedback(
                assignment_id=assignment.id
            )
        except Exception as e:
            print(str(e))
        else:
            return feedback

    """UNUSED FUNCTIONS maybe we can use them
    def get_cg_auto_test(client,assignment):
        try:
            test = client.assignment.get_auto_test(assignment_id=assignment.id)
        except Exception as e:
            print(str(e))
        else:
            return test
    """

    # COURSE SERVICE TYPES:
    def get_users(self, course):
        """Retrieves all users enrolled in a specified course.

        Args:
            course (object): The course object containing the course ID.

        Returns:
            list: A list of user objects enrolled in the course if successful.
            None: If an exception occurs during the API call.

        Raises:
            Exception: Logs the exception message if the API call fails.
        """
        try:
            users = self.client.course.get_all_users(course_id=course.id)
        except Exception as e:
            print(str(e))
        else:
            return users

    def get_all_user_submissions(self, course, user_id):
        """Retrieve all submissions made by a specific user in a given course.

        Args:
            course (object): The course object containing the course details.
            user_id (int): The unique identifier of the user whose submissions are to be retrieved.

        Returns:
            list: A list of submissions made by the user in the specified course,
                  or None if an exception occurs.

        Raises:
            Exception: If an error occurs during the API call, it is caught and printed.
        """
        # {'assignement_id':[extendedWork(...)]}
        try:
            users = self.client.course.get_submissions_by_user(
                course_id=course.id, user_id=user_id
            )
        except Exception as e:
            print(str(e))
        else:
            return users

    # SUBMISSION SERVICE TYPES:
    def get_rubric_grade(self, submission_id):
        """Retrieves the rubric grade for a given submission ID.

        Args:
            submission_id (int): The ID of the submission for which the rubric grade is to be retrieved.

        Returns:
            dict or None: The rubric grade as a dictionary if successfully retrieved,
                          or None if an exception occurs during the process.
        """
        try:
            grade = self.client.submission.get_rubric_result(
                submission_id=submission_id
            )
        except Exception as e:
            return None
        else:
            return grade

    # EXTRACTION
    def get_json_file(self, stud_dict, file_path):
        """Generates a JSON file from a given dictionary and saves it to the
        specified file path.

        Args:
            stud_dict (dict): The dictionary containing student data to be written to the JSON file.
            file_path (str): The directory path where the JSON file will be created.

        Returns:
            None: The function does not return a value. If the directory creation fails, the function exits early.

        Raises:
            OSError: If there is an issue writing to the file or creating the directory.

        Notes:
            - The JSON file is named ".cg-info.json" and will be created in the specified directory.
            - If the directory specified by `file_path` does not exist, it will attempt to create it using `self.mkdir(file_path)`.
            - Prints a message indicating the creation of the JSON file.
        """
        # file_name
        file_output = os.path.join(file_path, ".cg-info.json")
        print('Making json file ".cg-info.json"')
        # check if path exists
        if not self.mkdir(file_path):
            return
        with open(file_output, "w") as file:
            json.dump(stud_dict, file)

    def download_submission(self, submission, output_dir, *, retries=5):
        """Downloads a submission in ZIP format, extracts its contents, and
        saves them to a specified output directory. Retries the download in
        case of transient read errors.

        Args:
            submission (object): The submission object containing metadata about
                the submission, including the user or group information.
            output_dir (str): The directory where the extracted files will be saved.
            retries (int, optional): The number of retry attempts in case of a
                transient read error. Defaults to 5.

        Raises:
            httpx.ReadError: If the download fails after the specified number of retries.
            zipfile.BadZipFile: If the downloaded file is not a valid ZIP file.

        Notes:
            - If the submission is associated with a group, the output directory
              will include the group's name followed by "(Group)".
            - If the submission is associated with an individual user, the output
              directory will include the user's name.
            - Ensures that the output directory exists before extracting files.
            - Handles invalid ZIP files gracefully by printing an error message
              to stderr.
        """
        try:
            zipinfo = self.client.submission.get(
                submission_id=submission.id,
                type="zip",
            )
            # zipdata = client.file.download(filename=zipinfo['name'])
            zipdata = self.client.file.download(filename=zipinfo.name)

        except httpx.ReadError:
            # This is raised sometimes when doing a lot of simultaneous
            # downloads in a short amount of time.
            if not retries:
                raise
            time.sleep(1)
            return self.download_submission(
                self.client,
                submission,
                output_dir,
                retries=retries - 1,
            )

        if submission.user.group:
            username = submission.user.group.name + " (Group)"
        else:
            username = submission.user.name

        student_output_dir = os.path.join(output_dir, username)
        # C:\path\...\CS 472-Development-Businge-Assignment 3\Jacob Kasbohm

        if not self.mkdir(student_output_dir):
            return

        with zipfile.ZipFile(io.BytesIO(zipdata), "r") as zipf:
            try:
                for file in zipf.namelist():
                    filename = os.path.basename(file)
                    if not filename:
                        continue
                    source = zipf.open(file)
                    target = open(os.path.join(student_output_dir, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
            except zipfile.BadZipFile:
                print("Invalid zip file", file=sys.stderr)

    # helper function for extract_all_assignments
    def get_output_dir(self, course_name, assignment):
        """Generates the output directory path for a given course and
        assignment.

        Args:
            course_name (str): The name of the course.
            assignment (object): An object representing the assignment, which must have a 'name' attribute.

        Returns:
            str: The full path to the output directory for the specified course and assignment.
        """
        self.create_folder_path = os.path.join(os.getcwd(), "cg_data")
        fileName = course_name + " - " + assignment.name
        default_dir = os.path.join(self.create_folder_path, fileName)
        return default_dir

    # helper function for extract_all_assignments
    def get_sorted_dict(self, studDict):
        """Sorts and restructures the nested dictionaries within the provided
        student dictionary.

        This method takes a dictionary containing student data, sorts the items in the
        "submission_ids" and "user_ids" keys, and restructures the nested dictionaries
        for all keys in the input dictionary.

        Args:
            studDict (dict): A dictionary containing student data with keys "submission_ids",
                             "user_ids", and potentially other keys. Each key maps to a dictionary
                             of key-value pairs.

        Returns:
            dict: The input dictionary with "submission_ids" and "user_ids" sorted by their keys,
                  and all nested dictionaries restructured.
        """
        studDict["submission_ids"] = sorted(studDict["submission_ids"].items())
        studDict["user_ids"] = sorted(studDict["user_ids"].items())
        for key1 in studDict:
            currDict = {}
            for key, value in studDict[key1]:
                currDict[key] = value
            studDict[key1] = currDict
        return studDict

    # helper function for extract_all_assignments
    def make_zip_archive(self, zip_file_name, dir_path):
        """Creates a zip archive of a specified directory.

        This method takes the name of the output zip file and the path to the
        directory to be archived. It checks if the directory exists, and if so,
        creates a zip archive in the specified destination path. If the directory
        does not exist, it prints an error message and exits the function.

            zip_file_name (str): The name of the resulting output .zip file (without extension).
            dir_path (str): The path to the directory to be zipped.

        Returns:
            None
        """
        """Creates a zip archive of a directory.

        Args:
            zip_file_name (str): name of the resulting output .zip file
            dir_path (str): Path to the directory to be zipped.
        """
        if not os.path.exists(dir_path):
            print(
                f"Unable to create '{dir_path}.zip' due "
                f"to unfound '{zip_file_name}' directory name."
            )
            return
        destPath = os.path.join(self.create_folder_path, zip_file_name)
        # store into the new path instead of current dir
        shutil.make_archive(destPath, "zip", dir_path)
        # base_dir=zip_loc, root_dir=zip_loc, format='zip', base_name=zip_dest
        print(f"SUCCESS!! file '{zip_file_name}.zip' has been created!")
        # os.rename(os.path.splitext(zip_path)[0] + '.zip', zip_path)

    def extract_all_assignments(self, assignments):
        """
        INPUT PARAMS:
        assignemnts = assignments service from codegrade.
        DESC:
        Input all assignments from a course and create a zipfile

        NOTE:
        only look at the assignments who's lock_dates/deadlines
        are already past
        """
        print(f"Extracting all assignments from {self.course.name}:\n")
        for assignment in assignments:
            # get all submissions at current assignment
            submissions = self.client.assignment.get_all_submissions(
                assignment_id=assignment.id,
                latest_only=True,
            )
            # check if lockdate has past
            now = datetime.datetime.now()
            if assignment.lock_date:
                lock_date = datetime.datetime(
                    assignment.lock_date.year,
                    assignment.lock_date.month,
                    assignment.lock_date.day,
                    assignment.lock_date.hour,
                    assignment.lock_date.minute,
                    assignment.lock_date.second,
                )
            else:
                lock_date = datetime.datetime(
                    assignment.deadline.year,
                    assignment.deadline.month,
                    assignment.deadline.day,
                    assignment.deadline.hour,
                    assignment.deadline.minute,
                    assignment.deadline.second,
                )

            after_lock_date = lock_date < now
            if (len(submissions) > 0) & (after_lock_date):
                output_dir = self.get_output_dir(self.course.name, assignment)
                # output_dir = 'C:\\Users\\ejera\\testenv\\CS 472 - Development - Businge - Assignment 0'
                students = {"submission_ids": {}, "user_ids": {}}
                print(f"\nExtracting submission source code for {assignment.name}:")
                for submission in submissions:
                    # populate the students dictionary
                    subID = submission.id
                    stud_id_key = f"{subID} - {submission.user.name}"
                    stud_uid_key = f"{subID} - {submission.user.name}"
                    # local dictionary
                    userID = submission.user.id
                    students["submission_ids"][stud_id_key] = subID
                    students["user_ids"][stud_uid_key] = userID

                    # download all submissions and store them in the output_dir
                    print("Downloading", submission.user.name)
                    self.download_submission(submission, output_dir)
                # if there are more than one student
                students = self.get_sorted_dict(students)
                self.get_json_file(students, output_dir)
                # place json in file
                fileName = self.course.name + " - " + assignment.name
                print(f"{fileName} Successfully completed!")
                print(f'\nMaking "{fileName}" into a zip file')
                # convert directory made into a zip archive
                self.make_zip_archive(fileName, output_dir)
            elif not after_lock_date:
                print(
                    f"Lock date ({lock_date}) has not been passed yet for {assignment.name}"
                )
            else:
                print(f"No submissions for {assignment.name}")

    # helper fucntion for extract csv
    def get_grade(self, max_grade, grade_achieved):
        """Calculate the normalized grade based on the maximum grade and the
        grade achieved.

        Args:
            max_grade (float): The maximum possible grade for the assessment.
            grade_achieved (float): The grade achieved by the student.

        Returns:
            float: The normalized grade, scaled to a percentage (out of 100).
        """
        # assuming all the multipliers for each grade category is x1
        complement = 100 / max_grade
        return grade_achieved * complement

    def extract_csv(self, assignments):
        """
        INPUT PARAMS:
        assignemnts = assignments service from codegrade.
        DESC:
        Input all assignments from a course and create csv that has all information about
        the student submisison including stud-id, username, name, and grade.
        """
        print(
            f"\nExtracting .CSV file(s) for student(s) from class: '{self.course.name}'"
        )
        for assignment in assignments:
            submissions = self.client.assignment.get_all_submissions(
                assignment_id=assignment.id,
                latest_only=True,
            )
            # check if lockdate has past
            now = datetime.datetime.now()
            if assignment.lock_date:
                lock_date = datetime.datetime(
                    assignment.lock_date.year,
                    assignment.lock_date.month,
                    assignment.lock_date.day,
                    assignment.lock_date.hour,
                    assignment.lock_date.minute,
                    assignment.lock_date.second,
                )
            else:
                lock_date = datetime.datetime(
                    assignment.deadline.year,
                    assignment.deadline.month,
                    assignment.deadline.day,
                    assignment.deadline.hour,
                    assignment.deadline.minute,
                    assignment.deadline.second,
                )

            after_lock_date = lock_date < now
            if (len(submissions) > 0) & after_lock_date:
                # always create first row
                rows = ["Id", "Username", "Name", "Grade"]

                file_name = self.get_output_dir(self.course.name, assignment)
                file_name = file_name + ".csv"
                # find file_name
                fileCSV = open(file_name, "w", newline="")
                # open csv file - dont create a csv file unless there are submissions for
                # the assignment
                writer = csv.writer(fileCSV)
                # write the first row
                writer.writerow(rows)
                self.get_feedback(assignment)
                for submission in submissions:
                    grade = self.get_grade(assignment.max_grade, submission.grade)
                    # find the grade
                    rows = [
                        submission.user.id,
                        submission.user.username,
                        submission.user.name,
                        grade,
                    ]
                    writer.writerow(rows)
                print(
                    "SUCCESS!!! Create file 'CS 472 - Development - Businge - Assignment 4.csv' has been created!"
                )
                # close csv file
                fileCSV.close()
            elif not after_lock_date:
                print(
                    f"Lock date ({lock_date}) has not been passed yet for {assignment.name}"
                )
            else:
                print(f"No submissions for {assignment.name}")

    def delete_created_folder(self):
        """Deletes the folder specified by `self.create_folder_path` and its
        contents.

        This method attempts to remove the directory and all its contents. If the
        directory does not exist, a `FileNotFoundError` is handled gracefully. If
        the user does not have the necessary permissions to delete the directory,
        a `PermissionError` is handled. Any other errors encountered during the
        deletion process are also caught and reported.

        Exceptions Handled:
            - FileNotFoundError: Raised if the directory does not exist.
            - PermissionError: Raised if the user lacks permissions to delete the directory.
            - OSError: Raised for other errors during the deletion process.

        Prints:
            - Success message if the directory is deleted successfully.
            - Error messages for specific exceptions encountered.
        """
        try:
            shutil.rmtree(self.create_folder_path)
            print(
                f"Directory '{self.create_folder_path}' and its contents deleted successfully."
            )
        except FileNotFoundError:
            print(f"Directory '{self.create_folder_path}' not found.")
        except PermissionError:
            print(f"You do not have permission to delete '{self.create_folder_path}'.")
        except OSError as e:
            print(f"Error deleting '{self.create_folder_path}': {e}")


def main():
    """Main function to handle the data extraction process from the CodeGrade
    API.

    Steps performed:
    1. Logs in the client using credentials provided via CLI or `.env` file.
    2. Extracts all assignments with a lock date in the past and downloads their submissions.
    3. Generates a CSV file containing assignment data with columns: [ID, Username, Name, Grade].
    4. Deletes any temporary folders created during the process.

    Note:
    - Ensure the `.env` file is updated with the correct `USERNAME` and `CG_PASSWORD` before running.
    - Alternatively, use the CLI login method provided by the `codegrade` library.

    Dependencies:
    - Requires the `codegrade` library for API interaction.
    - Assumes the presence of the `API_Data` class with methods for data extraction and cleanup.
    """
    # log in client
    # BEFORE RUNNING!!!!!!
    # EDIT THE .ENV FILE AND INPUT YOUR USERNAME AND PASSWORD FOR USERNAME AND CG_PASSWORD
    # OR USE THIS INSTEAD TO LOGIN:
    client = codegrade.login_from_cli()

    cg_data = API_Data(client)
    cg_data.extract_all_assignments(
        cg_data.assignments
    )  # download all submissions of every assignment witht the lockdate past
    cg_data.extract_csv(
        cg_data.assignments
    )  # extrace the csv file witht he columns [ID,Username,Name,Grade]
    cg_data.delete_created_folder()  # delete the created folder
    # print(cg_data.get_course_info())
    # print(cg_data.get_rubric_grades_dict(cg_data.assignments))


if __name__ == "__main__":
    main()
