"""Tests for the Assignments models."""

from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date

from assignments import models as assign_models
from courses import models as course_models


# Helper functions for creating required related objects.
def create_user(
    email="test@example.com",
    password="testpass",
    first_name="Test",
    last_name="User",
):
    """Helper function to create a user with the specified attributes.

    Args:
        email (str): The email address of the user. Defaults to "test@example.com".
        password (str): The password for the user. Defaults to "testpass".
        first_name (str): The first name of the user. Defaults to "Test".
        last_name (str): The last name of the user. Defaults to "User".

    Returns:
        User: An instance of the created user.
    """

    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def create_professor(**params):
    """Creates and returns a Professor instance.

    This helper function first creates a user with the provided parameters
    or default values, and then uses that user to create a Professor object.

    Args:
        **params: Arbitrary keyword arguments to override default user attributes.
            Supported keys include:
            - email (str): The email address of the user. Defaults to "prof@example.com".
            - password (str): The password for the user. Defaults to "testpass".
            - first_name (str): The first name of the user. Defaults to "Prof".
            - last_name (str): The last name of the user. Defaults to "One".

    Returns:
        Professor: A newly created Professor instance associated with the user.
    """
    """Helper to create a professor (requires a user)."""
    defaults = {
        "email": "prof@example.com",
        "password": "testpass",
        "first_name": "Prof",
        "last_name": "One",
    }
    defaults.update(params)
    user = create_user(**defaults)
    return course_models.Professor.objects.create(user=user)


def create_class(name="Test Class"):
    """Creates and returns a new instance of the Class model with the specified
    name.

    Args:
        name (str): The name of the class to be created. Defaults to "Test Class".

    Returns:
        Class: An instance of the Class model with the specified name.
    """
    return course_models.Class.objects.create(name=name)


class StudentModelTests(TestCase):
    """Unit tests for the Student model.

    Classes:
        StudentModelTests: Contains test cases for the Student model.
    Methods:
        test_student_str:
            Verifies the string representation of a Student instance.
            Ensures the __str__ method returns the expected format.
        test_student_unique_email_and_codeGrade:
            Tests the uniqueness constraints on the email and codeGrade_id fields.
            Ensures that creating a Student with a duplicate email or codeGrade_id
            raises an IntegrityError.
    """

    def test_student_str(self):
        """Test the string representation of the Student model.

        This test verifies that the __str__ method of the Student model
        returns the expected string format, which includes the student's
        full name and email address.
        Expected format:
        "FirstName LastName (email@example.com)"
        """

        student = assign_models.Student.objects.create(
            email="student@example.com",
            codeGrade_id=1001,
            username="studentuser",
            first_name="John",
            last_name="Doe",
        )
        expected = "John Doe (student@example.com)"
        self.assertEqual(str(student), expected)

    def test_student_unique_email_and_codeGrade(self):
        """Test the uniqueness constraints on the Student model for email and
        codeGrade_id.

        This test ensures that:
        - Attempting to create a Student with a duplicate email raises an IntegrityError.
        - Attempting to create a Student with a duplicate codeGrade_id raises an IntegrityError.

        Steps:
        1. Create a Student instance with a unique email and codeGrade_id.
        2. Attempt to create another Student with the same email but a different codeGrade_id,
           and verify that an IntegrityError is raised.
        3. Attempt to create another Student with a different email but the same codeGrade_id,
           and verify that an IntegrityError is raised.
        """
        """Test that duplicate emails or codeGrade_id raise errors."""
        assign_models.Student.objects.create(
            email="unique@example.com",
            codeGrade_id=2001,
            username="uniqueuser",
            first_name="Unique",
            last_name="Student",
        )
        # Duplicate email
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                assign_models.Student.objects.create(
                    email="unique@example.com",  # duplicate email
                    codeGrade_id=2002,
                    username="anotheruser",
                    first_name="Another",
                    last_name="Student",
                )
        # Duplicate codeGrade_id
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                assign_models.Student.objects.create(
                    email="another@example.com",
                    codeGrade_id=2001,  # duplicate codeGrade_id
                    username="anotheruser",
                    first_name="Another",
                    last_name="Student",
                )


class AssignmentModelTests(TestCase):
    """Unit tests for the Assignment model.

    Classes:
        AssignmentModelTests: Contains test cases for the Assignment model.
    Methods:
        setUp(self):
            Sets up the test environment by creating a professor, a class instance,
            and a due date for use in the test cases.
        test_assignment_str(self):
            Verifies the string representation of an Assignment instance matches
            the expected format.
        test_assignment_unique_together(self):
            Ensures that the combination of class_instance and assignment_number
            is unique, raising an IntegrityError if a duplicate is attempted.
    """

    """Tests for the Assignment model."""

    def setUp(self):
        """Set up the test environment for assignment model tests.

        This method initializes the following:
        - A professor instance using the `create_professor` helper function.
        - A class instance named "Biology 101" using the `create_class` helper function.
        - A due date set to January 1, 2023.

        These objects are used as test fixtures for the assignment model tests.
        """
        self.professor = create_professor()
        self.test_class = create_class(name="Biology 101")
        self.due_date = date(2023, 1, 1)

    def test_assignment_str(self):
        """Test the string representation of the Assignment model.

        This test ensures that the `__str__` method of the Assignment model
        returns the expected string format, which includes the assignment
        number and title.
        """
        assignment = assign_models.Assignment.objects.create(
            class_instance=self.test_class,
            professor=self.professor,
            assignment_number=1,
            title="Test Assignment",
            due_date=self.due_date,
        )
        expected = "Assignment 1: Test Assignment"
        self.assertEqual(str(assignment), expected)

    def test_assignment_unique_together(self):
        """Tests the unique constraint on the Assignment model to ensure that
        assignments with the same `assignment_number` cannot be created for the
        same `class_instance` and `professor`.

        Steps:
        1. Create an initial Assignment object with a specific `assignment_number`.
        2. Attempt to create another Assignment object with the same `assignment_number`,
           `class_instance`, and `professor`.
        3. Verify that an IntegrityError is raised due to the unique constraint.
        This test ensures data integrity by preventing duplicate assignment numbers
        within the same class and professor context.
        """

        assign_models.Assignment.objects.create(
            class_instance=self.test_class,
            professor=self.professor,
            assignment_number=1,
            title="First Assignment",
            due_date=self.due_date,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                assign_models.Assignment.objects.create(
                    class_instance=self.test_class,
                    professor=self.professor,
                    assignment_number=1,
                    title="Duplicate Assignment Number",
                    due_date=self.due_date,
                )


class SubmissionModelTests(TestCase):
    """Tests for the Submission model.

    Classes:
        SubmissionModelTests: Contains unit tests for the Submission model.
    Methods:
        setUp:
            Sets up the test environment by creating a professor, class, assignment,
            and student for use in the tests.
        test_submission_str:
            Tests the string representation of a Submission instance to ensure it
            matches the expected format.
        test_submission_grade_validators:
            Tests the grade validation logic to ensure that grades outside the
            valid range (0-100) raise a ValidationError.
    """

    def setUp(self):
        """Set up the test environment for assignment models.

        This method initializes the following objects:
        - A professor instance using the `create_professor` helper function.
        - A class instance named "Chemistry 101" using the `create_class` helper function.
        - An assignment instance associated with the created class and professor, with a due date of February 1, 2023.
        - A student instance with specified email, codeGrade ID, username, first name, and last name.

        These objects are used to test the functionality of the assignment models.
        """
        self.professor = create_professor()
        self.test_class = create_class(name="Chemistry 101")
        self.due_date = date(2023, 2, 1)
        self.assignment = assign_models.Assignment.objects.create(
            class_instance=self.test_class,
            professor=self.professor,
            assignment_number=1,
            title="Chemistry Assignment",
            due_date=self.due_date,
        )
        self.student = assign_models.Student.objects.create(
            email="student2@example.com",
            codeGrade_id=3001,
            username="student2",
            first_name="Alice",
            last_name="Wonder",
        )

    def test_submission_str(self):
        """Tests the string representation of the Submission model.

        This test verifies that the __str__ method of the Submission
        model returns the expected string format, which includes the
        student's name and the assignment's name.
        """

        submission = assign_models.Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            grade=85,
            flagged=False,
            professor=self.professor,
        )
        expected = f"Submission by {self.student} for {self.assignment}"
        self.assertEqual(str(submission), expected)

    def test_submission_grade_validators(self):
        """Test case for validating the grade field in the Submission model.

        This test ensures that the `grade` field in the `Submission` model
        adheres to the defined validation rules. Specifically, it verifies
        that an invalid grade value (e.g., 150) raises a `ValidationError`
        when `full_clean()` is called on the model instance.
        """

        submission = assign_models.Submission(
            student=self.student,
            assignment=self.assignment,
            grade=150,  # invalid grade
            flagged=False,
            professor=self.professor,
        )
        with self.assertRaises(ValidationError):
            submission.full_clean()


class FlaggedSubmissionModelTests(TestCase):
    """
    Tests for the FlaggedSubmission model.
    This test case includes the following tests:
    1. `test_flagged_submission_str`: Verifies the string representation of a
        FlaggedSubmission instance, ensuring it matches the expected format.
    2. `test_flagged_submission_percentage_validators`: Ensures that the
        percentage field in a FlaggedSubmission instance adheres to the
        validation constraints (must be between 20 and 100).
    Setup:
    - Creates a professor, a class, an assignment, a student, and a submission
      to establish the necessary relationships for testing the FlaggedSubmission model.
    """

    def setUp(self):
        """Set up the test environment for assignment models.

        This method initializes the following objects:
        - A professor instance using the `create_professor` helper function.
        - A class instance named "Physics 101" using the `create_class` helper function.
        - An assignment instance associated with the professor and class, with a due date of March 1, 2023.
        - A student instance with specified email, username, and personal details.
        - A submission instance linking the student to the assignment, with a grade of 90, flagged as true, and associated with the professor.

        These objects are used to test the functionality of the assignment models.
        """
        self.professor = create_professor()
        self.test_class = create_class(name="Physics 101")
        self.due_date = date(2023, 3, 1)
        self.assignment = assign_models.Assignment.objects.create(
            class_instance=self.test_class,
            professor=self.professor,
            assignment_number=1,
            title="Physics Assignment",
            due_date=self.due_date,
        )
        self.student = assign_models.Student.objects.create(
            email="student3@example.com",
            codeGrade_id=4001,
            username="student3",
            first_name="Bob",
            last_name="Builder",
        )
        self.submission = assign_models.Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            grade=90,
            flagged=True,
            professor=self.professor,
        )

    def test_flagged_submission_str(self):
        """Test the string representation of the FlaggedSubmission model.

        This test verifies that the __str__ method of the
        FlaggedSubmission model returns the expected string format,
        which includes the file name and the percentage value. It also
        ensures that the similarity relation with a student can be added
        successfully.
        """

        flagged = assign_models.FlaggedSubmission.objects.create(
            submission=self.submission,
            file_name="plagiarism_report.pdf",
            percentage=80,
        )
        # Add a similarity relation to the student.
        flagged.similarity_with.add(self.student)
        expected = "Flagged Submission: plagiarism_report.pdf (80%)"
        self.assertEqual(str(flagged), expected)

    def test_flagged_submission_percentage_validators(self):
        """Test the validation of the `percentage` field in the
        `FlaggedSubmission` model. This test ensures that a `ValidationError`
        is raised when the `percentage` value is below the minimum allowed
        threshold (e.g., 20). The test creates a `FlaggedSubmission` instance
        with an invalid `percentage` value and calls the `full_clean` method to
        trigger validation.

        Expected Behavior:
        - A `ValidationError` is raised when the `percentage` is less than the
          minimum allowed value.
        """

        flagged = assign_models.FlaggedSubmission(
            submission=self.submission,
            file_name="low_similarity.pdf",
            percentage=10,  # below minimum of 20
        )
        with self.assertRaises(ValidationError):
            flagged.full_clean()


class FlaggedStudentModelTests(TestCase):
    """Tests for the FlaggedStudent model.

    This test case ensures the proper functionality of the FlaggedStudent model,
    including its string representation.
    Classes:
        FlaggedStudentModelTests: Contains unit tests for the FlaggedStudent model.
    Methods:
        setUp:
            Sets up the test environment by creating a professor and a student
            instance to be used in the tests.
        test_flagged_student_str:
            Tests the string representation of the FlaggedStudent model to ensure
            it matches the expected format.
    """

    def setUp(self):
        """Set up the test environment for assignment models.

        This method initializes the necessary objects for testing:
        - Creates a professor instance using the `create_professor` helper function.
        - Creates a student instance with predefined attributes, including email, codeGrade_id,
          username, first name, and last name, using the `Student` model.
        """
        self.professor = create_professor()
        self.student = assign_models.Student.objects.create(
            email="student4@example.com",
            codeGrade_id=5001,
            username="student4",
            first_name="Carol",
            last_name="Danvers",
        )

    def test_flagged_student_str(self):
        """Test the string representation of the FlaggedStudent model.

        This test ensures that the __str__ method of the FlaggedStudent
        model returns the expected string format, which includes the
        student's name and the number of times they have been flagged
        over the threshold.
        """
        """Test string representation of FlaggedStudent."""
        flagged_student = assign_models.FlaggedStudent.objects.create(
            student=self.student,
            professor=self.professor,
            times_over_threshold=3,
        )
        expected = f"Flagged Student: {self.student} flagged 3 times"
        self.assertEqual(str(flagged_student), expected)


class ConfirmedCheaterModelTests(TestCase):
    """Unit tests for the ConfirmedCheater model.

    This test case includes:
    - Setting up test data for a professor and a student.
    - Verifying the string representation of the ConfirmedCheater model.
    Classes:
    - ConfirmedCheaterModelTests: Contains tests for the ConfirmedCheater model.
    Methods:
    - setUp: Prepares test data for the professor and student.
    - test_confirmed_cheater_str: Tests the string representation of a ConfirmedCheater instance.
    """

    def setUp(self):
        """Set up the test environment for assignment models.

        This method initializes the necessary objects for testing:
        - Creates a professor instance using the `create_professor` helper function.
        - Creates a student instance with specified attributes, including email, codeGrade_id,
          username, first name, and last name, using the `assign_models.Student` model.
        """
        self.professor = create_professor()
        self.student = assign_models.Student.objects.create(
            email="student5@example.com",
            codeGrade_id=6001,
            username="student5",
            first_name="Dave",
            last_name="Grohl",
        )

    def test_confirmed_cheater_str(self):
        """Test the string representation of the ConfirmedCheater model.

        This test verifies that the __str__ method of the
        ConfirmedCheater model returns the expected string format, which
        includes the student's name, the confirmation date, and the
        threshold used for confirmation.
        """

        confirmed = assign_models.ConfirmedCheater.objects.create(
            student=self.student, professor=self.professor, threshold_used=50
        )
        expected = (
            f"Confirmed Cheater: {self.student} "
            f"on {confirmed.confirmed_date} (Threshold: 50%)"
        )
        self.assertEqual(str(confirmed), expected)
