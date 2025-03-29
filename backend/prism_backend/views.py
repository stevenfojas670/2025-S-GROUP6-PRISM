from .serializers import GoogleAuthSerializer
from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.views import LoginView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class GoogleAuthView(APIView):
    """A view for handling Google authentication.

    This view allows users to authenticate using Google OAuth and sets
    JWT cookies for access and refresh tokens upon successful authentication.
    Attributes:
        permission_classes (list): Specifies the permissions required to access this view.
                                   In this case, it allows any user to access.
        throttle_scope (str): Defines the throttle scope for rate limiting.
        serializer_class (GoogleAuthSerializer): The serializer used to validate the
                                                 incoming request data.
    Methods:
        post(request: Request):
            Handles POST requests for Google authentication.
            Validates the request data using the serializer, retrieves the access
            and refresh tokens, and sets them as cookies in the response.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth"
    serializer_class = GoogleAuthSerializer

    def post(self, request: Request):
        """Handles POST requests to authenticate a user and set JWT cookies.

        Args:
            request (Request): The HTTP request object containing user credentials.
        Returns:
            Response: A response object containing validated data and HTTP status 200.
                      JWT access and refresh tokens are set as cookies in the response.
        Raises:
            ValidationError: If the serializer data is invalid.
        """
        # Retrieve the request
        serializer = self.serializer_class(data=request.data)

        # Check if serializer is valid
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # The token is in this response, create a new response so we don't
        # expose the actual token to the client
        response = Response(data, status=status.HTTP_200_OK)

        set_jwt_cookies(
            response=response,
            access_token=data["access"],
            refresh_token=data["refresh"],
        )

        return response


class CustomLoginView(LoginView):
    """CustomLoginView extends the default LoginView to include additional
    functionality.

    Attributes:
        throttle_scope (str): Defines the scope for throttling login attempts.
                              This is used to limit the rate of login requests
                              to prevent abuse or brute-force attacks.
    """

    throttle_scope = "auth"
