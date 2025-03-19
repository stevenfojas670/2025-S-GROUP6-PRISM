"""
Views for the User APIs.
"""
#Views define how we handle requests
#rest_framework handles a lot of the logic we need to create objects in our database for us
#it does that by providing a bunch of base classes that we can configure for our views that will handle the request
#in a default standarize way, also it give us the ability to override some of that behavior so we can modify it if we need it
from users import serializers, models
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
