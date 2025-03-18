from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.request import Request
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_request
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.cache import cache
from dotenv import load_dotenv
import os
import time

load_dotenv()

GOOGLE_PUBLIC_KEYS_URL = "https://www.googleapis.com/oauth2/v3/certs"
CACHE_TIMEOUT = 3600
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
User = get_user_model()


@api_view(["POST"])
def validate_token(request: Request):
    token = request.data.get("token")

    if not token:
        return Response({"error": "Token is missing."}, status=400)

    try:
        print("Decoding token")
        # Validate the token against Google's Public Key
        decoded_token = id_token.verify_oauth2_token(
            id_token=token,
            request=google_auth_request.Request(),
            audience=GOOGLE_CLIENT_ID,
        )

        print("Token decoded")
        email = decoded_token["email"]
        if not email:
            return Response({"error": "User not found."}, status=400)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Access denied. User not registered."}, status=403
            )

        # Logging in with Django session authentication
        login(request, user)

        return Response(
            {
                "message": "User authenticated",
                "user_id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=200,
        )

    except ValueError:
        return Response({"error": "Invalid token"}, status=401)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
