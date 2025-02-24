"""
User Views APIs.
"""
from users import models, serializers
from courses.models import Professor
from rest_framework import viewsets

class UserVS(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def perform_create(self, serializer):
        # First, create the user instance using the serializer and
        #save the instance in 'user' variable
        user = serializer.save()
        # Then, create a corresponding Professor instance using the 'user' instance
        Professor.objects.create(user=user)

