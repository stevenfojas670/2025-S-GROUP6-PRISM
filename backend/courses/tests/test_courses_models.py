"""Tests for the Courses models."""

from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from courses import models as course_models


def create_user(
    email="test@example.com",
    password="testpass",
    first_name="Test",
    last_name="User",
):
    """Helper function to create a test user.

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


class ModelTests(TestCase):
    """ModelTests is a test case class that contains unit tests for various
    models in the courses application.

    These tests ensure the correctness of model
    behaviors, including string representations, relationships, and constraints.
    Methods:
        test_professor_str:
            Verifies the string representation of the Professor model, ensuring
            it returns the full name of the associated user.
        test_class_str:
            Verifies the string representation of the Class model, ensuring it
            returns the class name.
        test_semester_str:
            Verifies the string representation of the Semester model, ensuring it
            returns the semester name.
        test_professor_class_section_str:
            Verifies the string representation of the ProfessorClassSection model,
            ensuring it returns a formatted string combining professor, class,
            semester, and section number.
        test_class_professors_relationship:
            Tests the many-to-many relationship between Class and Professor via
            the ProfessorClassSection model, ensuring professors are correctly
            associated with classes.
        test_class_unique_name:
            Ensures that Class names are unique by testing the database constraint
            that prevents duplicate class names.
        test_semester_unique_name:
            Ensures that Semester names are unique by testing the database
            constraint that prevents duplicate semester names.
    """

    def test_professor_str(self):
        """Test the string representation of the Professor model.

        This test ensures that the __str__ method of the Professor model
        returns the expected string, which is a combination of the first
        name and last name of the associated user.
        """
        user = create_user(first_name="Alice", last_name="Smith")
        professor = course_models.Professor.objects.create(user=user)
        expected_str = f"{user.first_name} {user.last_name}"
        self.assertEqual(str(professor), expected_str)

    def test_class_str(self):
        """Test the string representation of the Class model.

        This test ensures that the __str__ method of the Class model
        returns the expected string representation, which is the name of
        the class.
        """
        class_obj = course_models.Class.objects.create(name="Math 101")
        self.assertEqual(str(class_obj), "Math 101")

    def test_semester_str(self):
        """Test the string representation of the Semester model.

        This test ensures that the __str__ method of the Semester model
        returns the correct string representation, which is the name of
        the semester.
        """
        semester = course_models.Semester.objects.create(name="Fall 2023")
        self.assertEqual(str(semester), "Fall 2023")

    def test_professor_class_section_str(self):
        """Test the string representation of the ProfessorClassSection model.

        This test verifies that the __str__ method of the ProfessorClassSection model
        returns the expected string format, which includes the professor's name,
        the class name, the semester, and the section number.

        Steps:
        1. Create a user with a first and last name.
        2. Create a Professor instance associated with the user.
        3. Create a Class instance with a specific name.
        4. Create a Semester instance with a specific name.
        5. Create a ProfessorClassSection instance with the professor, class, semester,
           and section number.
        6. Construct the expected string representation.
        7. Assert that the string representation of the ProfessorClassSection instance
           matches the expected string.
        """
        user = create_user(first_name="John", last_name="Doe")
        professor = course_models.Professor.objects.create(user=user)
        class_obj = course_models.Class.objects.create(name="History 101")
        semester = course_models.Semester.objects.create(name="Spring 2023")
        section_number = 3
        section = course_models.ProfessorClassSection.objects.create(
            professor=professor,
            class_instance=class_obj,
            semester=semester,
            section_number=section_number,
        )
        expected_str = (
            f"{professor} - {class_obj} - {semester} " f"(Section {section_number})"
        )
        self.assertEqual(str(section), expected_str)

    def test_class_professors_relationship(self):
        """Test the many-to-many relationship between Class and Professor
        models through the ProfessorClassSection model.

        This test verifies that a professor can be associated with a class
        for a specific semester and section number, and that the relationship
        is correctly reflected in the Class model's `professors` field.

        Steps:
        1. Create a user and associate it with a Professor instance.
        2. Create a Class instance and a Semester instance.
        3. Establish the relationship between the Professor, Class, and Semester
           using the ProfessorClassSection model.
        4. Assert that the professor is included in the Class model's `professors`
           many-to-many field.
        """
        user = create_user(first_name="Bob", last_name="Brown")
        professor = course_models.Professor.objects.create(user=user)
        class_obj = course_models.Class.objects.create(name="Biology 101")
        semester = course_models.Semester.objects.create(name="Winter 2023")
        # Create the mapping through the ProfessorClassSection model.
        course_models.ProfessorClassSection.objects.create(
            professor=professor,
            class_instance=class_obj,
            semester=semester,
            section_number=1,
        )
        # The many-to-many relationship should include our professor.
        self.assertIn(professor, class_obj.professors.all())

    def test_class_unique_name(self):
        """Tests that creating a `Class` object with a duplicate name raises an
        IntegrityError.

        This test ensures that the `name` field in the `Class` model is unique. It first
        creates a `Class` object with a specific name and then attempts to create another
        `Class` object with the same name. The test expects an `IntegrityError` to be raised
        during the second creation attempt.
        """
        course_models.Class.objects.create(name="UniqueClass")
        with self.assertRaises(IntegrityError):
            # Attempting to create another Class with the same name should fail
            course_models.Class.objects.create(name="UniqueClass")

    def test_semester_unique_name(self):
        """Tests that the Semester model enforces a unique constraint on the
        'name' field.

        This test creates a Semester instance with a specific name and
        then attempts to create another Semester instance with the same
        name. It verifies that an IntegrityError is raised, ensuring
        that duplicate names are not allowed.
        """
        course_models.Semester.objects.create(name="UniqueSemester")
        with self.assertRaises(IntegrityError):
            course_models.Semester.objects.create(name="UniqueSemester")
