"""
User Model Serializers.
"""
from rest_framework import serializers
from users import models

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'is_admin']
        extra_kwargs = {'is_admin': {'read_only': True}}

    def create(self, validated_data):
        #the entrance in the database is not the password but the hash
        password = validated_data.pop('password')
        user = models.User(**validated_data)
        user.set_password(password)
        user.save()
        return user