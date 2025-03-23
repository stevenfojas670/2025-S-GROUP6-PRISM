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
    id_token = serializers.CharField()

    def validate(self, attrs: dict):
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
                "refresh": "",
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
