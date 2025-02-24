"""
User URLs.
"""
from rest_framework.routers import DefaultRouter
from users.views import UserVS
from django.urls import path, include

user_router = DefaultRouter()
user_router.register('users', UserVS, basename='user-urls')

urlpatterns = [
    path('', include(user_router.urls)),
]