"""Tests for the Courses API endpoints."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from courses.models import Professor, Semester, Class, ProfessorClassSection


# Helper function to create a user (for Professor)
def create_user(
    email="test@example.com",
    password="pass123",
    first_name="Test",
    last_name="User",
):
    """
    Creates and returns a new user with the specified email, password,
    first name, and last name.

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


# Helper function to create a Professor instance
def create_professor(email, first_name, last_name):
    """
    Creates and returns a Professor instance.

    This function first creates a user with the provided email, first name,
    and last name, along with a default password. Then, it creates a
    Professor object associated with the created user.

    Args:
        email (str): The email address of the professor.
        first_name (str): The first name of the professor.
        last_name (str): The last name of the professor.

    Returns:
        Professor: The created Professor instance.
    """
    user = create_user(
        email=email,
        password="pass123",
        first_name=first_name,
        last_name=last_name,
    )
    return Professor.objects.create(user=user)


class ProfessorAPITests(APITestCase):
    """
    ProfessorAPITests(APITestCase)
    --------------------------------
    This test class contains unit tests for the Professor API endpoints. It ensures
    that the API behaves as expected when performing operations such as listing,
    filtering, ordering, and searching for professors.
    Methods:
    --------
    - setUp():
        Sets up the test environment by creating two sample professor objects.
    - test_list_professors():
        Verifies that the API correctly retrieves a list of all professors.
    - test_filter_professors_by_first_name():
        Tests the filtering functionality of the API by filtering professors based
        on their first name.
    - test_ordering_professors():
        Ensures that the API supports ordering professors in descending order by
        their first name.
    - test_search_professors():
        Confirms that the API allows searching for professors by their first name.
    """
    """Tests for the Professor API endpoints."""

    def setUp(self):
        """
        Set up the test environment for the courses API tests.

        This method creates two professor instances:
        - `self.prof1`: A professor with the email "john@example.com", first name "John", and last name "Doe".
        - `self.prof2`: A professor with the email "jane@example.com", first name "Jane", and last name "Smith".

        These instances are used in the test cases to simulate interactions with the courses API.
        """
        self.prof1 = create_professor("john@example.com", "John", "Doe")
        self.prof2 = create_professor("jane@example.com", "Jane", "Smith")

    def test_list_professors(self):
        """
        Test case for retrieving a list of professors.

        This test ensures that the API endpoint for listing professors
        returns a successful HTTP 200 response and that the number of
        professors in the response matches the expected count.
        """
        url = reverse("professor-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_professors_by_first_name(self):
        """
        Test filtering professors by their first name.
        This test ensures that the API endpoint for listing professors can filter
        results based on the `user__first_name` query parameter. It verifies that
        the response contains only the professors whose first name matches the
        specified value.
        Steps:
        1. Construct the URL with the query parameter `user__first_name=Jane`.
        2. Send a GET request to the `professor-list` endpoint.
        3. Assert that the response status code is 200 (OK).
        4. Assert that the response contains exactly one professor.
        5. Assert that the first name of the returned professor is "Jane".
        """

        url = reverse("professor-list") + "?user__first_name=Jane"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["user"]["first_name"], "Jane")

    def test_ordering_professors(self):
        """
        Test the ordering of professors by their first names in descending order.
        This test verifies that the API endpoint for listing professors correctly
        orders the results based on the `user__first_name` field in descending order
        when the `ordering=-user__first_name` query parameter is provided.
        Steps:
        1. Construct the URL for the professor list endpoint with the ordering parameter.
        2. Send a GET request to the endpoint.
        3. Assert that the response status code is 200 (OK).
        4. Extract the `first_name` values from the response data.
        5. Assert that the extracted first names are sorted in descending order.
        """

        url = reverse("professor-list") + "?ordering=-user__first_name"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        first_names = [item["user"]["first_name"] for item in res.data]
        self.assertEqual(first_names, sorted(first_names, reverse=True))

    def test_search_professors(self):
        """
        Test case for searching professors by their first name.

        This test verifies that the API endpoint for listing professors
        supports searching by the first name. It sends a GET request with
        a search query parameter and checks the following:

        - The response status code is 200 (HTTP_200_OK).
        - At least one professor in the response data has the first name
          matching the search query ("John").
        """
        url = reverse("professor-list") + "?search=John"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(any("John" in item["user"]["first_name"] for item in res.data))


class SemesterAPITests(APITestCase):
    """
    SemesterAPITests(APITestCase)
    -----------------------------
    This test class contains unit tests for the Semester API endpoints. It ensures
    that the API behaves as expected when listing, filtering, and searching for
    semesters.
    Methods:
        setUp():
            Sets up the test environment by creating two Semester objects:
            "Fall 2023" and "Spring 2023".
        test_list_semesters():
            Tests the retrieval of a list of all semesters. Verifies that the
            response status code is 200 (OK) and that the correct number of
            semesters is returned.
        test_filter_semesters_by_name():
            Tests filtering semesters by their name. Verifies that the response
            status code is 200 (OK), and that the filtered result matches the
            expected semester name.
        test_search_semesters():
            Tests searching for semesters using a query string. Verifies that the
            response status code is 200 (OK), and that the search result matches
            the expected semester name.
    """

    def setUp(self):
        """
        Set up the test environment for the courses API tests.

        This method creates two Semester objects:
        - `sem1`: Represents the "Fall 2023" semester.
        - `sem2`: Represents the "Spring 2023" semester.

        These objects are used as test data for validating the functionality
        of the courses API.
        """
        self.sem1 = Semester.objects.create(name="Fall 2023")
        self.sem2 = Semester.objects.create(name="Spring 2023")

    def test_list_semesters(self):
        """
        Test the API endpoint for retrieving a list of semesters.

        This test ensures that the `semester-list` endpoint returns a
        successful HTTP 200 response and that the number of semesters
        in the response matches the expected count.

        Steps:
        1. Reverse the URL for the `semester-list` endpoint.
        2. Perform a GET request to the endpoint.
        3. Assert that the response status code is HTTP 200 OK.
        4. Assert that the length of the response data is 2.

        Expected Outcome:
        - The API should return a status code of 200.
        - The response data should contain exactly 2 semesters.
        """
        url = reverse("semester-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_semesters_by_name(self):
        """
        Test filtering semesters by name.
        This test ensures that the API endpoint for listing semesters can filter
        semesters based on their name. It sends a GET request with a query parameter
        specifying the semester name and verifies the following:
        - The response status code is 200 (HTTP_200_OK).
        - The response contains exactly one semester.
        - The name of the returned semester matches the queried name ("Fall 2023").
        """

        url = reverse("semester-list") + "?name=Fall 2023"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Fall 2023")

    def test_search_semesters(self):
        """
        Test the search functionality for semesters in the API.
        This test verifies that the API correctly filters and returns semesters
        based on a search query. Specifically, it checks that:
        - The API endpoint returns a 200 OK status code.
        - The first result in the response matches the expected semester name.
        Steps:
        1. Construct the URL for the semester list endpoint with a search query.
        2. Perform a GET request to the constructed URL.
        3. Assert that the response status code is 200.
        4. Assert that the first semester in the response matches the expected name.
        Expected Result:
        - The API should return a list of semesters filtered by the search term.
        - The first semester in the list should match the expected name "Spring 2023".
        """

        url = reverse("semester-list") + "?search=Spring"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["name"], "Spring 2023")


class ClassAPITests(APITestCase):
    """Tests for the Class API endpoints."""

    def setUp(self):
        self.class1 = Class.objects.create(name="Math 101")
        self.class2 = Class.objects.create(name="History 101")

    def test_list_classes(self):
        """Test retrieving a list of classes."""
        url = reverse("class-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_search_classes(self):
        """Test searching for a class by name."""
        url = reverse("class-list") + "?search=Math"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Math 101")


class ProfessorClassSectionAPITests(APITestCase):
    """Tests for the ProfessorClassSection API endpoints."""

    def setUp(self):
        # Create two professors
        self.prof1 = create_professor("alice@example.com", "Alice", "Wonderland")
        self.prof2 = create_professor("bob@example.com", "Bob", "Builder")
        # Create a semester and a class
        self.semester = Semester.objects.create(name="Fall 2023")
        self.class_obj = Class.objects.create(name="Physics 101")
        # Create two ProfessorClassSection instances
        self.section1 = ProfessorClassSection.objects.create(
            professor=self.prof1,
            class_instance=self.class_obj,
            semester=self.semester,
            section_number=1,
        )
        self.section2 = ProfessorClassSection.objects.create(
            professor=self.prof2,
            class_instance=self.class_obj,
            semester=self.semester,
            section_number=2,
        )

    def test_list_professor_class_sections(self):
        """Test retrieving a list of professor class sections."""
        url = reverse("sectionclassprof-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_by_semester_name(self):
        """Test filtering professor class sections by semester name."""
        url = reverse("sectionclassprof-list") + "?semester__name=Fall 2023"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_search_professor_class_sections(self):
        """Test searching professor class sections by class name."""
        url = reverse("sectionclassprof-list") + "?search=Physics"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Expect both sections to match since they use the same class name.
        self.assertEqual(len(res.data), 2)
