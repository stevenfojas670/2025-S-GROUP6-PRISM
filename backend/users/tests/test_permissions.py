"""Test for permissions"""

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
    """Tests for user permission helpers and classes."""

    def setUp(self):
        self.factory = APIRequestFactory()
        # Create groups for Professor and TA
        self.professor_group = Group.objects.create(name="Professor")
        self.ta_group = Group.objects.create(name="TA")

    #
    # Helper function tests
    #
    def test_is_professor_true(self):
        user = get_user_model().objects.create_user(
            email="prof@example.com", password="testpass"
        )
        user.groups.add(self.professor_group)
        self.assertTrue(is_professor(user))

    def test_is_professor_false(self):
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_professor(user))

    def test_is_ta_true(self):
        user = get_user_model().objects.create_user(
            email="ta@example.com", password="testpass"
        )
        user.groups.add(self.ta_group)
        self.assertTrue(is_ta(user))

    def test_is_ta_false(self):
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_ta(user))

    def test_is_admin_staff(self):
        user = get_user_model().objects.create_user(
            email="staff@example.com", password="testpass", is_staff=True
        )
        self.assertTrue(is_admin(user))

    def test_is_admin_superuser(self):
        user = get_user_model().objects.create_superuser(
            email="super@example.com", password="testpass"
        )
        self.assertTrue(is_admin(user))

    def test_is_admin_false(self):
        user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpass"
        )
        self.assertFalse(is_admin(user))

    #
    # Permission class tests
    #
    def test_is_professor_or_ta_professor(self):
        """User is in Professor group => has permission."""
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
