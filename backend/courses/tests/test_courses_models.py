"""
Tests for the Courses models.
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from courses import models as course_models

def create_user(email='test@example.com', password='testpass', first_name='Test', last_name='User'):
    """Helper function to create a test user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

class ModelTests(TestCase):
    def test_professor_str(self):
        """Test the string representation of the Professor model."""
        user = create_user(first_name='Alice', last_name='Smith')
        professor = course_models.Professor.objects.create(user=user)
        expected_str = f"{user.first_name} {user.last_name}"
        self.assertEqual(str(professor), expected_str)

    def test_class_str(self):
        """Test the string representation of the Class model."""
        class_obj = course_models.Class.objects.create(name="Math 101")
        self.assertEqual(str(class_obj), "Math 101")

    def test_semester_str(self):
        """Test the string representation of the Semester model."""
        semester = course_models.Semester.objects.create(name="Fall 2023")
        self.assertEqual(str(semester), "Fall 2023")

    def test_professor_class_section_str(self):
        """Test the string representation of the ProfessorClassSection model."""
        user = create_user(first_name="John", last_name="Doe")
        professor = course_models.Professor.objects.create(user=user)
        class_obj = course_models.Class.objects.create(name="History 101")
        semester = course_models.Semester.objects.create(name="Spring 2023")
        section_number = 3
        section = course_models.ProfessorClassSection.objects.create(
            professor=professor,
            class_instance=class_obj,
            semester=semester,
            section_number=section_number
        )
        expected_str = f"{professor} - {class_obj} - {semester} (Section {section_number})"
        self.assertEqual(str(section), expected_str)

    def test_class_professors_relationship(self):
        """Test the many-to-many relationship between Class and Professor via ProfessorClassSection."""
        user = create_user(first_name="Bob", last_name="Brown")
        professor = course_models.Professor.objects.create(user=user)
        class_obj = course_models.Class.objects.create(name="Biology 101")
        semester = course_models.Semester.objects.create(name="Winter 2023")
        # Create the mapping through the ProfessorClassSection model.
        course_models.ProfessorClassSection.objects.create(
            professor=professor,
            class_instance=class_obj,
            semester=semester,
            section_number=1
        )
        # The many-to-many relationship should include our professor.
        self.assertIn(professor, class_obj.professors.all())

    def test_class_unique_name(self):
        """Test that Class names must be unique."""
        course_models.Class.objects.create(name="UniqueClass")
        with self.assertRaises(IntegrityError):
            # Attempting to create another Class with the same name should fail.
            course_models.Class.objects.create(name="UniqueClass")

    def test_semester_unique_name(self):
        """Test that Semester names must be unique."""
        course_models.Semester.objects.create(name="UniqueSemester")
        with self.assertRaises(IntegrityError):
            course_models.Semester.objects.create(name="UniqueSemester")