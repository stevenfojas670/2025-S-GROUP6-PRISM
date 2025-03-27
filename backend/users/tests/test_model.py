"""
Tests for the User model.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

class UserModelTest(TestCase):
    """Test the user model."""

    def test_create_user_successfuly(self):
        """Test for creating a user is successful."""
        email = 'test@example.com'
        password = '123test'
        first_name = 'testName'
        last_name = 'testLast'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalization(self):
        """Test that email is normalized."""
        dummyEmails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['test5@ExamPle.Com', 'test5@example.com']
        ]

        for email, expectedEmail in dummyEmails:
            user = get_user_model().objects.create_user(
                email=email,
                password='sample123'
            )
            self.assertEqual(user.email, expectedEmail)

    def test_new_user_without_email_error(self):
        """Test creating a user without an email gives us a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='sample123',
                first_name='first',
                last_name='last'
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='test123',
            first_name='first',
            last_name='last'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)

    def test_update_user_fields(self):
        """Test updating user fields works correctly."""
        user = get_user_model().objects.create_user(
            email='update@example.com',
            password='pass123',
            first_name='Initial',
            last_name='Name'
        )
        user.first_name = 'Updated'
        user.last_name = 'User'
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'User')

    def test_unique_email_constraint(self):
        """Test that creating a user with an existing email raises an error."""
        email = 'unique@example.com'
        get_user_model().objects.create_user(
            email=email,
            password='pass123',
            first_name='Unique',
            last_name='User'
        )
        with self.assertRaises(IntegrityError):
            # Attempt to create a duplicate user; this should fail.
            get_user_model().objects.create_user(
                email=email,
                password='pass456',
                first_name='Duplicate',
                last_name='User'
            )

    def test_minimal_valid_input_defaults(self):
        """Test creating a user with minimal valid input and checking default values."""
        user = get_user_model().objects.create_user(
            email='minimal@example.com',
            password='minpass',
            first_name='Min',
            last_name='User'
        )
        self.assertTrue(user.is_active)   # Typically active by default.
        self.assertFalse(user.is_staff)    # Assuming non-staff by default.
        self.assertFalse(user.is_superuser)