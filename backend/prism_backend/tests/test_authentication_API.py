"""Test the Courses API endpoints.

This file tests the viewsets for the Prism_Backend app for authentication
and deauthentication functionality.
"""

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from courses.models import (
    Professors,
)

User = get_user_model()


class BaseAuthAPITest(APITestCase):
    """Base test case for authentication API tests.

    Sets up common objects required for API endpoint tests.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for the authentication API tests."""
        cls.professor_user = User.objects.create_user(
            username="prof1",
            password="pass123",
            email="professor@example.com",
        )
        cls.professor = Professors.objects.create(user=cls.professor_user)


class AuthenticationViewTest(BaseAuthAPITest):
    """Tests for GoogleAuthView, CustomLoginView, and CustomLogoutView."""

    def test_login_existing_user(self):
        """Test for logging in with an existing user."""
        # Perform JWT login
        login_response = self.client.post(
            "/api/login",
            {"username": self.professor_user.email, "password": "pass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200, msg=login_response.json())

        data = login_response.json()

        # Check if the prism-access cookie is set
        self.assertIn("prism-access", login_response.cookies)
        self.assertTrue(login_response.cookies["prism-access"].value)

        # Check if the prism-refresh cookie is set
        self.assertIn("prism-refresh", login_response.cookies)
        self.assertTrue(login_response.cookies["prism-refresh"].value)

        # Check if the cookie is HttpOnly and has expected attributes
        self.assertTrue(login_response.cookies["prism-access"]["httponly"])
        self.assertTrue(login_response.cookies["prism-refresh"]["httponly"])

        # Check if user is returned in the response
        self.assertEqual(self.professor_user.email, data["user"]["email"])

    def test_login_invalid_user(self):
        """Test for logging in with an invalid user."""
        # Perform JWT login
        login_response = self.client.post(
            "/api/login",
            {"username": self.professor_user.email, "password": "WrongPassword"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 400, msg=login_response.json())
        data = login_response.json()
        self.assertEqual(
            data["non_field_errors"][0], "Unable to log in with provided credentials."
        )

    def test_logout_logged_in_user(self):
        """Test for logging out currently logged in user."""
        # Perform JWT login
        login_response = self.client.post(
            "/api/login",
            {"username": self.professor_user.email, "password": "pass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200, msg=login_response.json())

        # Ensure tokens are created
        self.assertIn("prism-access", login_response.cookies)
        self.assertIn("prism-refresh", login_response.cookies)

        # Set cookies in client for logout request
        self.client.cookies["prism-access"] = login_response.cookies[
            "prism-access"
        ].value
        self.client.cookies["prism-refresh"] = login_response.cookies[
            "prism-refresh"
        ].value

        # Now log out
        logout_response = self.client.post("/api/logout")
        self.assertEqual(logout_response.status_code, 200, msg=logout_response.json())
        self.assertEqual(logout_response.data["detail"], "Successfully logged out.")

    def test_logout_no_user(self):
        """Test logging out for no logged in user."""
        logout_response = self.client.post("/api/logout")
        self.assertEqual(logout_response.status_code, 200, msg=logout_response.json())
        self.assertEqual(logout_response.data["detail"], "Successfully logged out.")
