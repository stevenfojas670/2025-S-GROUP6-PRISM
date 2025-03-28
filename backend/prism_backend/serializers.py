from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

User = get_user_model()


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for handling Google OAuth2 authentication.

    Attributes:
        id_token (serializers.CharField): A required field for the Google ID token.
    Methods:
        validate(attrs: dict):
            Validates the provided Google ID token, verifies its authenticity, and retrieves user information.
            If the token is valid and the user exists in the database, generates and returns JWT tokens
            (access and refresh) along with user details and token expiration times.
            Args:
                attrs (dict): A dictionary containing the ID token.
            Returns:
                dict: A dictionary containing the access token, refresh token, user details, and token expiration times.
            Raises:
                serializers.ValidationError: If the token is invalid or the email is missing from the Google token.
    """

    id_token = serializers.CharField()

    def validate(self, attrs: dict):
        """Validates the provided attributes by verifying the Google ID token
        and generating JWT tokens for the user.

        Args:
            attrs (dict): A dictionary containing the attributes to validate.
                          Expected to include the "id_token" key.
        Returns:
            dict: A dictionary containing the generated access and refresh tokens,
                  user details (primary key, email, first name, last name),
                  and token expiration timestamps.
        Raises:
            serializers.ValidationError: If the Google ID token is invalid,
                                         does not contain an email,
                                         or if the user does not exist.
        """
        id_token_str = attrs.get("id_token")
        try:
            # Verify Google's id_token
            google_info = id_token.verify_oauth2_token(
                id_token=id_token_str,
                request=requests.Request(),
                audience=os.getenv("GOOGLE_CLIENT_ID"),
            )

            if "email" not in google_info:
                raise serializers.ValidationError("Invalid Google token.")

            # Check if the user exists
            email = google_info["email"]
            user = User.objects.get(email=email)

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            access_exp = (
                datetime.fromtimestamp(access_token["exp"], tz=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
            refresh_exp = (
                datetime.fromtimestamp(refresh["exp"], tz=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )

            # Returning the newly created token to the view
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "pk": user.pk,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "access_expiration": access_exp,
                "refresh_expiration": refresh_exp,
            }
        except ValueError:
            raise serializers.ValidationError("Invalid token.")
