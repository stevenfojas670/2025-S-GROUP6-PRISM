"""
Views for the User APIs.
"""

# Views define how we handle requests
# rest_framework handles a lot of the logic we need to create objects in our database for us
# it does that by providing a bunch of base classes that we can configure for our views that will handle the request
# in a default standarize way, also it give us the ability to override some of that behavior so we can modify it if we need it
from users import models, serializers
from courses.models import Professor
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend


class UserVS(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "id",
        "first_name",
        "last_name",
        "email",
    ]

    # def get_queryset(self):
    #     user = self.request.user
    #     return models.User.objects.get(pk=user.pk)

    def perform_create(self, serializer):
        """Create a user and automatically assign them as a Professor."""
        user = serializer.save()
        Professor.objects.create(user=user)
