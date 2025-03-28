"""Tests for the Assignments API endpoints."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import date

from assignments.models import (
    Student,
    Assignment,
    Submission,
    FlaggedSubmission,
    FlaggedStudent,
    ConfirmedCheater,
)
from courses.models import Professor, Class as CourseClass


# Helper functions to create required objects.
def create_user(
    email="test@example.com",
    password="pass123",
    first_name="Test",
    last_name="User",
):
    """Creates and returns a new user with the specified email, password, first
    name, and last name.

    Args:
        email (str): The email address of the user. Defaults to "test@example.com".
        password (str): The password for the user. Defaults to "pass123".
        first_name (str): The first name of the user. Defaults to "Test".
        last_name (str): The last name of the user. Defaults to "User".

    Returns:
        User: The created user instance.
    """
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def create_professor(email="prof@example.com", first_name="Prof", last_name="One"):
    """Creates and returns a Professor instance with an associated User.

    Args:
        email (str): The email address for the professor's user account. Defaults to "prof@example.com".
        first_name (str): The first name of the professor. Defaults to "Prof".
        last_name (str): The last name of the professor. Defaults to "One".

    Returns:
        Professor: A newly created Professor instance.
    """
    user = create_user(
        email=email,
        password="pass123",
        first_name=first_name,
        last_name=last_name,
    )
    return Professor.objects.create(user=user)


def create_course_class(name="Test Class"):
    """Creates and returns a CourseClass instance with the specified name.

    Args:
        name (str): The name of the CourseClass to create. Defaults to "Test Class".

    Returns:
        CourseClass: The created CourseClass instance.
    """
    return CourseClass.objects.create(name=name)


# ----- Student API Tests -----
class StudentAPITests(APITestCase):
    """Test suite for the Student API endpoints.

    This test class contains unit tests for verifying the functionality of the
    Student API, including listing all students and searching for specific students
    based on query parameters.
    Classes:
        StudentAPITests: A test case class that uses Django's APITestCase to test
        the Student API endpoints.
    Methods:
        setUp():
            Sets up the test environment by creating sample Student objects to be
            used in the test cases.
        test_list_students():
            Tests the "student-list" endpoint to ensure it returns a 200 OK status
            and the correct number of students.
        test_search_students():
            Tests the "student-list" endpoint with a search query to ensure it
            returns a 200 OK status and the correct student data matching the query.
    """

    def setUp(self):
        """SetUp method to initialize test data for the assignments API tests.

        This method creates two Student objects with the following attributes:
        - student1:
            - email: "student1@example.com"
            - codeGrade_id: 1001
            - username: "stud1"
            - first_name: "Alice"
            - last_name: "Anderson"
        - student2:
            - email: "student2@example.com"
            - codeGrade_id: 1002
            - username: "stud2"
            - first_name: "Bob"
            - last_name: "Brown"

        These objects are used as test data for validating the functionality of the API.
        """
        self.student1 = Student.objects.create(
            email="student1@example.com",
            codeGrade_id=1001,
            username="stud1",
            first_name="Alice",
            last_name="Anderson",
        )
        self.student2 = Student.objects.create(
            email="student2@example.com",
            codeGrade_id=1002,
            username="stud2",
            first_name="Bob",
            last_name="Brown",
        )

    def test_list_students(self):
        """Test case for listing students via the API.

        This test ensures that the "student-list" endpoint returns a 200 OK status
        and that the number of students in the response matches the expected count.

        Assertions:
            - The HTTP status code of the response is 200 (OK).
            - The length of the response data is 2.
        """
        url = reverse("student-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_search_students(self):
        """Test case for searching students by name.

        This test verifies that the API endpoint for searching students
        returns the correct results when a query parameter is provided.

        Steps:
        1. Construct the URL with a search query for "Alice".
        2. Send a GET request to the student-list endpoint.
        3. Assert that the response status code is 200 (HTTP_200_OK).
        4. Assert that the response contains exactly one student.
        5. Assert that the first name of the returned student is "Alice".
        """
        url = reverse("student-list") + "?search=Alice"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["first_name"], "Alice")


# ----- Flagged Student API Tests -----
class FlaggedStudentAPITests(APITestCase):
    """Test suite for the FlaggedStudent API endpoints.

    This test class contains unit tests for the FlaggedStudent API, ensuring that
    the endpoints for listing and filtering flagged students function as expected.
    Methods:
        setUp():
            Sets up the test environment by creating a professor, a student, and
            a flagged student instance for use in the tests.
        test_list_flagged_students():
            Tests the "flagged-student-list" endpoint to ensure it returns a
            successful response and the correct number of flagged students.
        test_filter_flagged_students():
            Tests the "flagged-student-list" endpoint with a filter query to ensure
            it returns a successful response and the correct flagged student data
            based on the professor's ID.
    """

    def setUp(self):
        """Set up the test environment for the assignments API tests.

        This method initializes the following:
        - A professor instance with specified email, first name, and last name.
        - A student instance with specified email, codeGrade ID, username, first name, and last name.
        - A flagged student instance linking the student and professor, with a specified number of times over the threshold.
        """
        self.prof = create_professor(
            email="prof1@example.com", first_name="Jane", last_name="Doe"
        )
        self.student = Student.objects.create(
            email="student3@example.com",
            codeGrade_id=1003,
            username="stud3",
            first_name="Charlie",
            last_name="Chaplin",
        )
        self.flagged_student = FlaggedStudent.objects.create(
            student=self.student, professor=self.prof, times_over_threshold=5
        )

    def test_list_flagged_students(self):
        """Test case for retrieving the list of flagged students.

        This test ensures that the API endpoint for fetching flagged students
        returns a 200 OK status and that the response contains the expected
        number of flagged students.

        Assertions:
            - The HTTP status code of the response is 200 (OK).
            - The number of flagged students in the response data matches the expected count.
        """
        url = reverse("flagged-student-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_flagged_students(self):
        """Test case for filtering flagged students by professor ID.

        This test verifies that the API endpoint for retrieving flagged students
        returns the correct data when filtered by a specific professor's ID.

        Steps:
        1. Construct the URL for the "flagged-student-list" endpoint with a query
           parameter for the professor's ID.
        2. Send a GET request to the constructed URL.
        3. Assert that the response status code is HTTP 200 OK.
        4. Assert that the response contains exactly one flagged student.
        5. Assert that the flagged student's "times_over_threshold" value is 5.
        """
        url = reverse("flagged-student-list") + f"?professor__id={self.prof.id}"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["times_over_threshold"], 5)


# ----- Assignment API Tests -----
class AssignmentAPITests(APITestCase):
    """Test suite for the Assignment API. This test class contains unit tests
    for the Assignment API endpoints, ensuring that the API behaves as expected
    for listing, filtering, and searching assignments.

    Test Cases:
    - `test_list_assignments`: Verifies that the API returns a list of all assignments
        with the correct status code and data length.
    - `test_filter_assignments_by_title`: Ensures that the API can filter assignments
        by their title and return the correct assignment.
    - `test_search_assignments`: Confirms that the API supports searching assignments
        by a keyword and returns the expected results.
    Setup:
    - Creates a professor, a course class, and two assignments to be used in the tests.
    """

    def setUp(self):
        """Set up the test environment for the assignments API tests.

        This method creates the following test data:
        - A professor with the email "prof2@example.com" and the name "John Doe".
        - A course class named "Math 101".
        - Two assignments associated with the course class and professor:
            1. "Algebra Assignment" with a due date of May 1, 2023.
            2. "Geometry Assignment" with a due date of May 15, 2023.
        """
        self.prof = create_professor(
            email="prof2@example.com", first_name="John", last_name="Doe"
        )
        self.course_class = create_course_class(name="Math 101")
        self.assignment1 = Assignment.objects.create(
            class_instance=self.course_class,
            professor=self.prof,
            assignment_number=1,
            title="Algebra Assignment",
            due_date=date(2023, 5, 1),
        )
        self.assignment2 = Assignment.objects.create(
            class_instance=self.course_class,
            professor=self.prof,
            assignment_number=2,
            title="Geometry Assignment",
            due_date=date(2023, 5, 15),
        )

    def test_list_assignments(self):
        """Test case for listing assignments via the API.

        This test ensures that the API endpoint for retrieving a list of assignments
        returns a 200 OK status and the expected number of assignments.

        Steps:
        1. Reverse the URL for the "assignments-list" endpoint.
        2. Perform a GET request to the endpoint.
        3. Assert that the response status code is HTTP 200 OK.
        4. Assert that the number of assignments in the response matches the expected count.

        Expected Outcome:
        - The API should return a 200 OK status.
        - The response should contain exactly 2 assignments.
        """
        url = reverse("assignments-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_assignments_by_title(self):
        """Test filtering assignments by title.

        This test ensures that the API endpoint for listing assignments
        correctly filters assignments based on the provided title query parameter.

        Steps:
        1. Construct the URL with a query parameter for filtering by title.
        2. Send a GET request to the assignments-list endpoint.
        3. Verify that the response status code is HTTP 200 OK.
        4. Assert that the response contains exactly one assignment.
        5. Confirm that the title of the returned assignment matches the filter.

        Expected Outcome:
        - The API should return a single assignment with the title "Algebra Assignment".
        """
        url = reverse("assignments-list") + "?title=Algebra Assignment"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Algebra Assignment")

    def test_search_assignments(self):
        """Test the search functionality of the assignments API.

        This test verifies that the API correctly filters assignments based on a
        search query. It sends a GET request to the "assignments-list" endpoint
        with a search parameter and checks the following:

        - The response status code is 200 (HTTP_200_OK).
        - The number of assignments returned matches the expected count.
        - The assignment number of the first result matches the expected value.

        The search query used in this test is "Geometry".
        """
        url = reverse("assignments-list") + "?search=Geometry"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["assignment_number"], 2)


# ----- Submission API Tests -----
class SubmissionAPITests(APITestCase):
    """Test suite for the Submission API.

    This test class contains unit tests for the Submission API endpoints, ensuring
    that the functionality for listing, filtering, and searching submissions works
    as expected.
    Methods:
        setUp():
            Sets up the test environment by creating a professor, course class,
            assignment, student, and two submissions for testing purposes.
        test_list_submissions():
            Tests the endpoint for listing all submissions. Verifies that the
            response status is 200 OK and that the correct number of submissions
            is returned.
        test_filter_submissions_by_flagged():
            Tests the endpoint for filtering submissions by the "flagged" status.
            Verifies that the response status is 200 OK, the correct number of
            flagged submissions is returned, and that the flagged status is True.
        test_search_submissions():
            Tests the endpoint for searching submissions by assignment title.
            Verifies that the response status is 200 OK and that the assignment
            title in the response matches the search query.
    """

    def setUp(self):
        """Set up the test environment for the assignments API tests.

        This method initializes the following objects:
        - A professor instance with specified email, first name, and last name.
        - A course class instance with a specified name.
        - An assignment instance associated with the course class and professor,
          including assignment details such as number, title, and due date.
        - A student instance with specified email, codeGrade ID, username, first name, and last name.
        - Two submission instances associated with the student and assignment:
            - The first submission has a grade of 88 and is not flagged.
            - The second submission has a grade of 92 and is flagged.

        These objects are used to test various functionalities of the assignments API.
        """
        self.prof = create_professor(
            email="prof3@example.com", first_name="Alice", last_name="Smith"
        )
        self.course_class = create_course_class(name="History 101")
        self.assignment = Assignment.objects.create(
            class_instance=self.course_class,
            professor=self.prof,
            assignment_number=1,
            title="World History Assignment",
            due_date=date(2023, 6, 1),
        )
        self.student = Student.objects.create(
            email="student4@example.com",
            codeGrade_id=1004,
            username="stud4",
            first_name="David",
            last_name="Dunn",
        )
        self.submission1 = Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            grade=88,
            flagged=False,
            professor=self.prof,
        )
        self.submission2 = Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            grade=92,
            flagged=True,
            professor=self.prof,
        )

    def test_list_submissions(self):
        """Test the API endpoint for listing submissions.

        This test verifies that the submissions-list endpoint returns a
        successful HTTP 200 response and that the number of submissions
        in the response matches the expected count.

        Assertions:
            - The HTTP status code of the response is 200 (OK).
            - The length of the response data is 2.
        """
        url = reverse("submissions-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_submissions_by_flagged(self):
        """Test case for filtering submissions by the 'flagged' status.

        This test ensures that the API endpoint correctly filters and returns
        only the submissions that are flagged when the 'flagged=True' query
        parameter is provided.

        Steps:
        1. Construct the URL for the submissions list endpoint with the
           'flagged=True' query parameter.
        2. Perform a GET request to the constructed URL.
        3. Assert that the response status code is HTTP 200 OK.
        4. Assert that the response contains exactly one submission.
        5. Assert that the returned submission has the 'flagged' attribute set to True.
        """
        url = reverse("submissions-list") + "?flagged=True"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertTrue(res.data[0]["flagged"])

    def test_search_submissions(self):
        """Test the search functionality for submissions.

        This test verifies that the API endpoint for searching submissions
        returns the correct results when queried with a specific search term.

        Steps:
        1. Construct the URL with a search query parameter for "World History".
        2. Send a GET request to the submissions-list endpoint.
        3. Assert that the response status code is HTTP 200 OK.
        4. Validate that the first result in the response contains an assignment
           with the title "World History Assignment".

        Expected Outcome:
        - The API should return a successful response with the correct data
          matching the search query.
        """
        url = reverse("submissions-list") + "?search=World History"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify nested assignment title in the response.
        self.assertEqual(res.data[0]["assignment"]["title"], "World History Assignment")


# ----- Flagged Submission API Tests -----
class FlaggedSubmissionAPITests(APITestCase):
    """Test suite for the FlaggedSubmission API. This test class contains unit
    tests for verifying the functionality of the FlaggedSubmission API
    endpoints. It includes tests for listing flagged submissions, filtering
    them by percentage, and searching by file name.

    Test Cases:
    - `test_list_flagged_submissions`: Ensures that the API returns a list of flagged
        submissions with the correct status code and data length.
    - `test_filter_flagged_submissions_by_percentage`: Verifies that the API can filter
        flagged submissions based on the similarity percentage.
    - `test_search_flagged_submissions`: Confirms that the API supports searching flagged
        submissions by file name.
    Setup:
    - Creates a professor, course class, assignment, student, submission, and flagged
        submission as test data.
    - Associates the flagged submission with a student for similarity comparison.
    Dependencies:
    - Django REST Framework's `APITestCase` for API testing.
    - Models: `Assignment`, `Student`, `Submission`, `FlaggedSubmission`.
    - Utility functions: `create_professor`, `create_course_class`.
    """

    def setUp(self):
        """Set up the test environment for the assignments API tests.

        This method initializes the following objects:
        - A professor instance with specified email, first name, and last name.
        - A course class instance with a given name.
        - An assignment instance associated with the professor and course class,
          including assignment details such as number, title, and due date.
        - A student instance with specified email, codeGrade ID, username, first name,
          and last name.
        - A submission instance linked to the student and assignment, including grade,
          flagged status, and professor.
        - A flagged submission instance associated with the submission, including file
          name and similarity percentage. The flagged submission is also linked to the
          student for similarity tracking.
        """
        self.prof = create_professor(
            email="prof4@example.com", first_name="Emma", last_name="Stone"
        )
        self.course_class = create_course_class(name="Physics 101")
        self.assignment = Assignment.objects.create(
            class_instance=self.course_class,
            professor=self.prof,
            assignment_number=1,
            title="Quantum Mechanics",
            due_date=date(2023, 7, 1),
        )
        self.student = Student.objects.create(
            email="student5@example.com",
            codeGrade_id=1005,
            username="stud5",
            first_name="Frank",
            last_name="Furter",
        )
        self.submission = Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            grade=95,
            flagged=True,
            professor=self.prof,
        )
        self.flagged_submission = FlaggedSubmission.objects.create(
            submission=self.submission, file_name="report.pdf", percentage=85
        )
        self.flagged_submission.similarity_with.add(self.student)

    def test_list_flagged_submissions(self):
        """Test case for retrieving the list of flagged submissions.

        This test ensures that the API endpoint for fetching flagged submissions
        returns a 200 OK status and that the response contains the expected number
        of flagged submissions.

        Assertions:
            - The HTTP status code of the response is 200 (OK).
            - The number of flagged submissions in the response matches the expected value.
        """
        url = reverse("flagged-submission-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_flagged_submissions_by_percentage(self):
        """Test the filtering of flagged submissions by percentage.

        This test ensures that the API endpoint for retrieving flagged submissions
        correctly filters the results based on the provided percentage query parameter.

        Steps:
        1. Construct the URL with the query parameter `percentage=85`.
        2. Send a GET request to the flagged submissions endpoint.
        3. Verify that the response status code is HTTP 200 OK.
        4. Assert that the response contains exactly one submission.
        5. Confirm that the percentage of the returned submission matches the filter value (85).

        Expected Outcome:
        - The API returns only the submissions that match the specified percentage.
        """
        url = reverse("flagged-submission-list") + "?percentage=85"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["percentage"], 85)

    def test_search_flagged_submissions(self):
        """Test the search functionality for flagged submissions.

        This test ensures that the API endpoint for retrieving flagged submissions
        correctly filters results based on a search query. Specifically, it verifies
        that a search for the term "report" returns the expected flagged submission
        with the file name "report.pdf".

        Steps:
        1. Construct the URL for the flagged submissions list endpoint with a search query.
        2. Perform a GET request to the constructed URL.
        3. Assert that the response status code is HTTP 200 OK.
        4. Assert that the first item in the response data matches the expected file name.

        Expected Outcome:
        - The API should return a status code of 200.
        - The flagged submission with the file name "report.pdf" should be included in the results.
        """
        url = reverse("flagged-submission-list") + "?search=report"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["file_name"], "report.pdf")


# ----- Confirmed Cheater API Tests -----
class ConfirmedCheaterAPITests(APITestCase):
    """
    Tests for the ConfirmedCheater API endpoints.
    This test suite includes the following test cases:
    1. `test_list_confirmed_cheaters`: Verifies that the API endpoint for listing all
        confirmed cheaters returns the correct status code and data.
    2. `test_filter_confirmed_cheaters_by_threshold`: Ensures that the API endpoint
        correctly filters confirmed cheaters based on the `threshold_used` parameter.
    3. `test_search_confirmed_cheaters`: Confirms that the API endpoint supports
        searching for confirmed cheaters by the professor's user first name.
    Setup:
    - Creates a professor and a student.
    - Creates a `ConfirmedCheater` instance linking the professor and student with
      a specific threshold value.
    Dependencies:
    - Django REST Framework's `APITestCase` for API testing.
    - Models: `Student`, `ConfirmedCheater`.
    - Utility function: `create_professor`.
    """

    def setUp(self):
        """SetUp method to initialize test data for the assignments API tests.

        This method creates the following test objects:
        - A professor instance with specified email, first name, and last name.
        - A student instance with specified email, codeGrade ID, username, first name, and last name.
        - A confirmed cheater instance linking the student and professor, with a specified threshold used.

        These objects are used to set up the necessary context for testing the assignments API.
        """
        self.prof = create_professor(
            email="prof5@example.com", first_name="Olivia", last_name="Newton"
        )
        self.student = Student.objects.create(
            email="student6@example.com",
            codeGrade_id=1006,
            username="stud6",
            first_name="George",
            last_name="Clooney",
        )
        self.confirmed_cheater = ConfirmedCheater.objects.create(
            student=self.student, professor=self.prof, threshold_used=45
        )

    def test_list_confirmed_cheaters(self):
        """Test the API endpoint for listing confirmed cheaters.

        This test ensures that the "confirmed-cheater-list" endpoint returns a
        successful HTTP 200 response and that the number of confirmed cheaters
        in the response data matches the expected value.

        Assertions:
            - The HTTP status code of the response is 200 (OK).
            - The length of the response data is 1.
        """
        url = reverse("confirmed-cheater-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_confirmed_cheaters_by_threshold(self):
        """Test the filtering of confirmed cheaters by a specified threshold.

        This test verifies that the API endpoint for retrieving confirmed cheaters
        correctly filters the results based on the provided threshold value.

        Steps:
        1. Send a GET request to the "confirmed-cheater-list" endpoint with a query
           parameter `threshold_used=45`.
        2. Assert that the response status code is HTTP 200 OK.
        3. Assert that the response data contains exactly one entry.
        4. Assert that the `threshold_used` field of the returned entry matches the
           specified threshold value (45).
        """
        url = reverse("confirmed-cheater-list") + "?threshold_used=45"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["threshold_used"], 45)

    def test_search_confirmed_cheaters(self):
        """Test case for searching confirmed cheaters by a professor's user
        first name.

        This test verifies that the API endpoint for listing confirmed cheaters
        supports searching by the professor's user first name. It ensures that:
        1. The API returns a 200 OK status code when a valid search query is provided.
        2. The response data contains the expected professor's user first name
           in the nested structure.

        Steps:
        - Perform a GET request to the "confirmed-cheater-list" endpoint with a
          search query for the professor's user first name.
        - Assert that the response status code is 200.
        - Assert that the expected first name is present in the response data.

        Endpoint: "confirmed-cheater-list"
        Query Parameter: search
        """
        # Searching on professor's user first name.
        url = reverse("confirmed-cheater-list") + "?search=Olivia"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify that the nested professor's user first name is returned.
        self.assertIn("Olivia", res.data[0]["professor"]["user"]["first_name"])
