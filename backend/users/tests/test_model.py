"""
Test for the User model.
"""
from django.test import TestCase
#best practice is to use this get_user_model function so it updates to whererver user model we using
from django.contrib.auth import get_user_model

class UserModelTest(TestCase):
    """Test the user model."""
    def test_create_user_successfuly(self):
        """Tes for creating an user is sucessful."""
        email = 'test@example.com'
        password = '123test'
        first_name = 'testName'
        last_name = 'testLast'
        user = get_user_model().objects.create_user(email=email, password=password,
                                                    first_name=first_name, last_name=last_name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalization(self):
        """Test that email is normalized."""
        dummyEmails = [ ['test1@EXAMPLE.com', 'test1@example.com'],
                        ['Test2@Example.com', 'Test2@example.com'],
                        ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
                        ['test4@example.COM', 'test4@example.com'],
                        ['test5@ExamPle.Com', 'test5@example.com']
        ]

        #loop trhough the dummyEmail list (email is the first parameter in the element and expectedEmail is the second one)
        #recall this is looping trhough a list of list so this is the python code for this scenario
        for email, expectedEmail in dummyEmails:

            #create an user with the dummyEmails examples (the not normalized ones)
            user = get_user_model().objects.create_user(email=email, password='sample123')

            #check if normalized emails are stored instead of the given ones
            self.assertEqual(user.email, expectedEmail)

    def test_new_user_without_email_error(self):
        """Test creating a user without an email gives us a ValueError."""

        #this code must raise a ValueError, if it does not or raises another kind of error this assert will fail
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password='sample123', first_name='first', last_name='last')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(email='test@example.com', password='test123', first_name='first', last_name='last')

        #.is_superuser is a field provided for 'PermissionsMixin' import
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)
