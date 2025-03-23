from .serializers import GoogleAuthSerializer
from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"
    serializer_class = GoogleAuthSerializer

    def post(self, request: Request):
        # Retrieve the request
        serializer = self.serializer_class(data=request.data)

        # Check if serializer is valid
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # The token is in this response, create a new response so we don't expose the actual token to the client
        response = Response(data, status=status.HTTP_200_OK)

        set_jwt_cookies(
            response=response,
            access_token=data["access"],
            refresh_token=data["refresh"],
        )

        # Return custom response to the user not exposing to token over the network response
        return response


class CustomLoginView(LoginView):
    throttle_scope = "auth"
