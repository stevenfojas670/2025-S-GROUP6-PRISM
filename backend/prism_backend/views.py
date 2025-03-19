import os
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_request
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from dotenv import load_dotenv
from datetime import datetime, timedelta
from prism_backend import serializers

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
User = get_user_model()
expiration_time = datetime.now() + timedelta(hours=24)


@api_view(["POST"])
@csrf_exempt
def login_view(request: Request):
    """Handling user logins"""

    print(request.data)

    serializer = serializers.LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]

    login(request._request, user)

    return Response(
        {"message": "Login successful.", "username": user.username},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def validate_token(request: Request):
    """Validating the user's access token sent from Google"""

    token = request.data.get("token")

    # Each time you deserialize, check if its valid
    if not token:
        return Response({"error": "Token is missing."}, status=400)

    try:
        # Validate the token against Google's Public Key
        # If the token is invalid, verify_oauth2_token() will raise a ValueError
        decoded_token = id_token.verify_oauth2_token(
            id_token=token,
            request=google_auth_request.Request(),
            audience=GOOGLE_CLIENT_ID,
        )

        # Validate that the user is in our database by email, since User emails are unique
        email = decoded_token["email"]

        if not email:
            return Response({"error": "User not found."}, status=400)

        # Check if the user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Access denied. User not registered."}, status=403
            )

        # Logging in with Django session authentication
        login(request._request, user)

        # We will use the csrf_token to prevent cross-site-request-forgery by setting it in the HTTP cookie
        csrf_token = get_token(request)

        # Returning a response to notify the user of success
        response = Response(
            {
                "message": "User authenticated",
                "email": user.email,
            },
            status=200,
        )

        # Setting the cookie
        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            expires=expiration_time,
        )

        """CSRF tokens are checked only when the user makes modifying requests such as POST, PUT, DELETE, and PATCH"""

        return response

    except ValueError:
        return Response({"error": "Invalid token"}, status=401)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
