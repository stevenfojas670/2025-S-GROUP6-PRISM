from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True, allow_blank=False)
    password = serializers.CharField(required=True, write_only=True, allow_blank=False)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        data["user"] = user

        return data
