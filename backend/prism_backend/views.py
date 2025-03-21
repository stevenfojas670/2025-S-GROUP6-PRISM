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
        response = Response(data, status=status.HTTP_200_OK)

        # Set the cookies so the user can access the jwt token
        set_jwt_cookies(
            response=response,
            access_token=data["access"],
            refresh_token=data["refresh"],
        )

        return response


class CustomLoginView(LoginView):
    throttle_scope = "auth"
