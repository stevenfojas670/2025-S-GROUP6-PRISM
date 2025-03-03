from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def hello_world(request):
    return Response({"message": "Hello from Django Rest Framework!"})

def validate_token(request):
    # Do token validation stuff
    print("token will be validated")