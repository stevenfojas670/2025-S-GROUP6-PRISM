"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

#user as an app and creeate as an endpoint (of our route/url)
#we save this url path in this constant cuz we will use it for many different tests
#user-list because by default Django router appends -list as a standard convention
CREATE_USER_URL = reverse('user:user-list')

#helper fucntion to create user since we will do this many many times to not repeat code over and over again
## **params allow us to pass any dictionary that contains parameters straight into the user
def create_user(**params):
    """Creates and return a new user."""
    return get_user_model().objects.create_user(**params)

#public will be for unauthenticated requests such as registering a new user
#private will be for authenticated requests
class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""
    def setUp(self):

        #this will create an APIClient that we can use for testing
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is succsesful."""

        #we will pass here (in a dictionary) all the info needed to create a new user
        #this is basically the body of the request to create a new user that we must handle
        # btw note that this is a JSON a string (basically)
        payload = {
            'email': 'test@example.com',
            'password': 'sample123',
            'first_name': 'Dummy',
            'last_name': 'lastDummy',
        }

        #we sent a POST request to the 'CREATE_USER_URL' url defined at the begining of the file with the 'payload' (request body) defined above
        res = self.client.post(CREATE_USER_URL, payload)

        #the success response code for creating objects in the database is 201 so we must check the response contains this code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #retrieves the object from the database with the 'email' field we pass in the payload of our request
        user = get_user_model().objects.get(email=payload['email'])

        #check if the password of the user retrieved above is the one specified in the payload of the request
        self.assertTrue(user.check_password(payload['password']))

        #makes sure there are no keyword = 'password' in the response (we dont want to send the password anywhere for security reasons)
        self.assertNotIn('password', res.data)

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email already exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'sample123',
            'first_name': 'Dummy',
            'last_name': 'lastDummy',
        }

        #this is whats nice about our helper fucntion, you give it a JSON string needed to create users and it will do it for you
        #we dont do it like this on the above fucntion because in that one we are actually testing if the user is created succsesfuly
        create_user(**payload)

        #since we created an user already with the payload information above this request should return an error because the user is already created
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'meh',
            'first_name': 'Dummy',
            'last_name': 'lastDummy',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        #if user exists in our database (if it was created with this way to short password) then error
        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        #it must be false
        self.assertFalse(user_exist)