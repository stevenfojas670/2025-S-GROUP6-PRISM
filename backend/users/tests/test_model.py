"""Tests for the User model."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class UserModelTest(TestCase):
    """Test suite for the User model.

    This test suite includes the following test cases:
    1. `test_create_user_successfuly`: Verifies that a user can be created successfully with valid input.
    2. `test_new_user_email_normalization`: Ensures that the email address is normalized (lowercased domain).
    3. `test_new_user_without_email_error`: Checks that creating a user without an email raises a `ValueError`.
    4. `test_create_superuser`: Confirms that a superuser can be created and has the correct permissions.
    5. `test_update_user_fields`: Tests that user fields can be updated and saved correctly.
    6. `test_unique_email_constraint`: Validates that creating a user with a duplicate email raises an `IntegrityError`.
    7. `test_minimal_valid_input_defaults`: Ensures that creating a user with minimal valid input sets the correct default values for fields like `is_active`, `is_staff`, and `is_superuser`.
    """

    def test_create_user_successfuly(self):
        """Test the successful creation of a user.

        This test verifies that a user can be created with the specified email,
        password, first name, and last name. It ensures that the created user's
        attributes match the provided values and that the password is correctly
        set and can be validated.
        """
        email = "test@example.com"
        password = "123test"
        first_name = "testName"
        last_name = "testLast"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalization(self):
        """Test the normalization of email addresses for new users. This test
        ensures that email addresses provided during user creation are properly
        normalized to a consistent format. It verifies that the email field of
        the created user matches the expected normalized email format.

        Test Cases:
            - A variety of email addresses with different cases and domain
              formats are tested to ensure proper normalization.
        Example:
            Input: "test1@EXAMPLE.com"
            Expected Output: "test1@example.com"
        """
        dummyEmails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
            ["test5@ExamPle.Com", "test5@example.com"],
        ]

        for email, expectedEmail in dummyEmails:
            user = get_user_model().objects.create_user(
                email=email, password="sample123"
            )
            self.assertEqual(user.email, expectedEmail)

    def test_new_user_without_email_error(self):
        """Test that creating a new user without an email raises a ValueError.

        This test ensures that the `create_user` method of the user model
        enforces the requirement for an email address. If an empty string
        is provided as the email, a `ValueError` should be raised.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email="",
                password="sample123",
                first_name="first",
                last_name="last",
            )

    def test_create_superuser(self):
        """Test the creation of a superuser.

        This test verifies that a superuser can be successfully created
        with the specified email, password, first name, and last name.
        It also ensures that the created user has the `is_superuser` and
        `is_admin` flags set to True.
        """
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="test123",
            first_name="first",
            last_name="last",
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)

    def test_update_user_fields(self):
        """Test case for updating user fields.

        This test verifies that the `first_name` and `last_name` fields of a user
        can be successfully updated and saved to the database. It ensures that
        the changes persist after refreshing the user instance from the database.

        Steps:
        1. Create a user with initial `first_name` and `last_name` values.
        2. Update the `first_name` and `last_name` fields of the user.
        3. Save the changes and refresh the user instance from the database.
        4. Assert that the updated values match the expected values.
        """
        user = get_user_model().objects.create_user(
            email="update@example.com",
            password="pass123",
            first_name="Initial",
            last_name="Name",
        )
        user.first_name = "Updated"
        user.last_name = "User"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")

    def test_unique_email_constraint(self):
        """Test to ensure that the email field in the user model is unique.

        This test creates a user with a specific email and then attempts to
        create another user with the same email. The second creation should
        raise an IntegrityError due to the unique constraint on the email
        field.
        """
        email = "unique@example.com"
        get_user_model().objects.create_user(
            email=email,
            password="pass123",
            first_name="Unique",
            last_name="User",
        )
        with self.assertRaises(IntegrityError):
            # Attempt to create a duplicate user; this should fail.
            get_user_model().objects.create_user(
                email=email,
                password="pass456",
                first_name="Duplicate",
                last_name="User",
            )

    def test_minimal_valid_input_defaults(self):
        """Test the creation of a minimal valid user with default values.

        This test ensures that a user created with minimal valid input
        has the correct default attributes:
        - `is_active` should be True.
        - `is_staff` should be False.
        - `is_superuser` should be False.
        """
        user = get_user_model().objects.create_user(
            email="minimal@example.com",
            password="minpass",
            first_name="Min",
            last_name="User",
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
