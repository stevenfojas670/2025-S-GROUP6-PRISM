"""Test for permissions."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from users.permissions import (
    is_professor,
    is_ta,
    is_admin,
    IsProfessorOrTA,
    IsProfessorOrAdmin,
    IsProfessor,
    IsAdmin,
)


class PermissionTests(TestCase):
    """PermissionTests is a test suite for verifying the behavior of helper
    functions and permission classes related to user roles and access control
    in the application.

    Test Cases:
    -----------
    1. Helper Function Tests:
        - `test_is_professor_true`: Verifies that a user in the "Professor" group is identified as a professor.
        - `test_is_professor_false`: Verifies that a user not in the "Professor" group is not identified as a professor.
        - `test_is_ta_true`: Verifies that a user in the "TA" group is identified as a teaching assistant.
        - `test_is_ta_false`: Verifies that a user not in the "TA" group is not identified as a teaching assistant.
        - `test_is_admin_staff`: Verifies that a staff user is identified as an admin.
        - `test_is_admin_superuser`: Verifies that a superuser is identified as an admin.
        - `test_is_admin_false`: Verifies that a regular user is not identified as an admin.

    2. Permission Class Tests:
        - `test_is_professor_or_ta_professor`: Verifies that a user in the "Professor" group has permission via `IsProfessorOrTA`.
        - `test_is_professor_or_ta_ta`: Verifies that a user in the "TA" group has permission via `IsProfessorOrTA`.
        - `test_is_professor_or_ta_none`: Verifies that a user in neither the "Professor" nor "TA" group does not have permission via `IsProfessorOrTA`.
        - `test_is_professor_or_admin_professor`: Verifies that a user in the "Professor" group has permission via `IsProfessorOrAdmin`.
        - `test_is_professor_or_admin_admin`: Verifies that an admin user has permission via `IsProfessorOrAdmin`.
        - `test_is_professor_or_admin_none`: Verifies that a user who is neither a professor nor an admin does not have permission via `IsProfessorOrAdmin`.
        - `test_is_professor_true`: Verifies that a user in the "Professor" group has permission via `IsProfessor`.
        - `test_is_professor_false`: Verifies that a user not in the "Professor" group does not have permission via `IsProfessor`.
        - `test_is_admin_true_staff`: Verifies that a staff user has permission via `IsAdmin`.
        - `test_is_admin_true_superuser`: Verifies that a superuser has permission via `IsAdmin`.
        - `test_is_admin_false`: Verifies that a regular user does not have permission via `IsAdmin`.

    Setup:
    ------
    - Creates an APIRequestFactory instance for generating mock requests.
    - Creates user groups for "Professor" and "TA" to test group-based permissions.

    Purpose:
    --------
    This test suite ensures that the helper functions and permission classes correctly
    identify user roles and enforce access control based on the application's requirements.
    """

    def setUp(self):
        """Set up the test environment for permission tests.

        This method initializes the APIRequestFactory for creating mock
        requests and sets up user groups for "Professor" and "TA" to be
        used in the tests.
        """
        self.factory = APIRequestFactory()
        # Create groups for Professor and TA
        self.professor_group = Group.objects.create(name="Professor")
        self.ta_group = Group.objects.create(name="TA")

    #
    # Helper function tests
    #
    def test_is_professor_true(self):
        """Test case for verifying the `is_professor` function.

        This test ensures that the `is_professor` function correctly identifies
        a user as a professor when the user is added to the professor group.

        Steps:
        1. Create a user with a valid email and password.
        2. Add the user to the professor group.
        3. Assert that the `is_professor` function returns True for the user.
        """
        user = get_user_model().objects.create_user(
            email="prof@example.com", password="testpass"
        )
        user.groups.add(self.professor_group)
        self.assertTrue(is_professor(user))

    def test_is_professor_false(self):
        """Test case for the `is_professor` function.

        This test verifies that the `is_professor` function correctly identifies
        a user who is not a professor. It creates a regular user and asserts
        that the function returns `False` for this user.
        """
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_professor(user))

    def test_is_ta_true(self):
        """Test case for verifying the `is_ta` function.

        This test ensures that the `is_ta` function correctly identifies a user
        as a teaching assistant (TA) when the user is added to the TA group.

        Steps:
        1. Create a user with a specified email and password.
        2. Add the user to the TA group.
        3. Assert that the `is_ta` function returns True for the user.

        Expected Result:
        The `is_ta` function should return True, indicating that the user
        is recognized as a teaching assistant.
        """
        user = get_user_model().objects.create_user(
            email="ta@example.com", password="testpass"
        )
        user.groups.add(self.ta_group)
        self.assertTrue(is_ta(user))

    def test_is_ta_false(self):
        """Test case for the `is_ta` function to verify it returns False for a
        regular user.

        This test creates a user with no teaching assistant (TA) privileges and asserts
        that the `is_ta` function correctly identifies the user as not being a TA.
        """
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_ta(user))

    def test_is_admin_staff(self):
        """Test to verify that the `is_admin` function correctly identifies a
        user with staff privileges as an admin.

        This test creates a user with `is_staff` set to True and asserts that
        the `is_admin` function returns True for this user.
        """
        user = get_user_model().objects.create_user(
            email="staff@example.com", password="testpass", is_staff=True
        )
        self.assertTrue(is_admin(user))

    def test_is_admin_superuser(self):
        """Test to verify that the `is_admin` function correctly identifies a
        superuser as an admin.

        This test creates a superuser using the `get_user_model` method and checks
        if the `is_admin` function returns `True` for the created superuser.
        """
        user = get_user_model().objects.create_superuser(
            email="super@example.com", password="testpass"
        )
        self.assertTrue(is_admin(user))

    def test_is_admin_false(self):
        """Test to verify that the `is_admin` function returns False for a
        regular user.

        This test creates a user with standard permissions and checks that the
        `is_admin` function correctly identifies the user as not having admin privileges.
        """
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_admin(user))

    #
    # Permission class tests
    #
    def test_is_professor_or_ta_professor(self):
        """Test case for the `IsProfessorOrTA` permission class.

        This test verifies that a user who belongs to the "professor" group
        is granted permission by the `IsProfessorOrTA` permission class.

        Steps:
        1. Create an instance of the `IsProfessorOrTA` permission class.
        2. Simulate a GET request using the test request factory.
        3. Create a user with a valid email and password.
        4. Add the user to the "professor" group.
        5. Assign the user to the request object.
        6. Assert that the `has_permission` method of the permission class
           returns `True` for the given request and view.

        Expected Outcome:
        The permission check should pass, indicating that users in the
        "professor" group have the required permissions.
        """
        permission = IsProfessorOrTA()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="prof@example.com", password="testpass"
        )
        user.groups.add(self.professor_group)
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_professor_or_ta_ta(self):
        """User is in TA group => has permission."""
        permission = IsProfessorOrTA()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="ta@example.com", password="testpass"
        )
        user.groups.add(self.ta_group)
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_professor_or_ta_none(self):
        """User is neither Professor nor TA => no permission."""
        permission = IsProfessorOrTA()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="none@example.com", password="testpass"
        )
        request.user = user

        self.assertFalse(permission.has_permission(request, None))

    def test_is_professor_or_admin_professor(self):
        """User is a Professor => has permission."""
        permission = IsProfessorOrAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="prof@example.com", password="testpass"
        )
        user.groups.add(self.professor_group)
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_professor_or_admin_admin(self):
        """User is an admin => has permission."""
        permission = IsProfessorOrAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_superuser(
            email="super@example.com", password="testpass"
        )
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_professor_or_admin_none(self):
        """User is neither Professor nor admin => no permission."""
        permission = IsProfessorOrAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="none@example.com", password="testpass"
        )
        request.user = user

        self.assertFalse(permission.has_permission(request, None))

    def test_is_professor_true(self):
        """User is in Professor group => has permission."""
        permission = IsProfessor()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="prof@example.com", password="testpass"
        )
        user.groups.add(self.professor_group)
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_professor_false(self):
        """User not in Professor group => no permission."""
        permission = IsProfessor()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="none@example.com", password="testpass"
        )
        request.user = user

        self.assertFalse(permission.has_permission(request, None))

    def test_is_admin_true_staff(self):
        """Staff user => has permission."""
        permission = IsAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="staff@example.com", password="testpass", is_staff=True
        )
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_admin_true_superuser(self):
        """Superuser => has permission."""
        permission = IsAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_superuser(
            email="super@example.com", password="testpass"
        )
        request.user = user

        self.assertTrue(permission.has_permission(request, None))

    def test_is_admin_false(self):
        """Regular user => no permission."""
        permission = IsAdmin()
        request = self.factory.get("/")
        user = get_user_model().objects.create_user(
            email="none@example.com", password="testpass"
        )
        request.user = user

        self.assertFalse(permission.has_permission(request, None))
