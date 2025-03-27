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
from django.db.models import Q


class UserVS(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def list(self, request: Request):
        queryset = models.User.objects.all()

        email = request.query_params.get("email")
        first_name = request.query_params.get("first_name")
        last_name = request.query_params.get("last_name")

        if email:
            queryset = queryset.filter(email__icontains=email)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        ordering = request.query_params.get("ordering", "first_name")
        queryset = queryset.order_by(ordering)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk=None):
        """Retrieve a single user by ID."""
        try:
            instance = models.User.objects.get(pk=pk)
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request: Request, pk=None):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer=serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def partial_update(self, request: Request, pk=None):

        try:
            instance = self.get_object()

            serializer = self.serializer_class(
                instance, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except models.User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        """Create a user and automatically assign them as a Professor."""
        user = serializer.save()
        Professor.objects.create(user=user)
