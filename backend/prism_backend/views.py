from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def hello_world(request):
    return Response({"message": "Hello from Django Rest Framework!"})

@api_view(["GET"])
def validate_token(request):
    return Response({"message": "VALIDATE TOKEN PATH CALLED"}, status=200)