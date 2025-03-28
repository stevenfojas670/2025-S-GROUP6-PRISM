from rest_framework.permissions import BasePermission
import logging

# used for logging access to views. This creates a 'logger' thats named based on this specific app (users.permissions)
logger = logging.getLogger(__name__)


# to be used by a view. Its up to us to decide what gets logged this way, and what specifically is passed as 'action' and 'resource'
def log_role_access(user, action, resource):
    logger.info(f"{user} performed {action} on {resource}")


# In users/permissions.py
def is_professor(user):
    return user.groups.filter(name="Professor").exists()


def is_ta(user):
    return user.groups.filter(name="TA").exists()


def is_admin(user):
    return user.is_staff or user.is_superuser


class IsProfessorOrTA(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (is_professor(request.user) or is_ta(request.user))
        )


class IsProfessorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (is_professor(request.user) or is_admin(request.user))
        )


# for more restrictive views
class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and is_professor(request.user)
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and is_admin(request.user)
        )
