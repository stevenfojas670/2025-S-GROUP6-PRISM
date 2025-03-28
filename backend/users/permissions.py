from rest_framework.permissions import BasePermission
import logging

# used for logging access to views. This creates a 'logger' thats named based on this specific app (users.permissions)
logger = logging.getLogger(__name__)


# to be used by a view. Its up to us to decide what gets logged this way, and what specifically is passed as 'action' and 'resource'
def log_role_access(user, action, resource):
    """Logs the access of a user performing an action on a specific resource.

    Args:
        user (str): The username or identifier of the user performing the action.
        action (str): The action performed by the user (e.g., "read", "write", "delete").
        resource (str): The resource on which the action is performed (e.g., file, database entry).

    Returns:
        None
    """
    logger.info(f"{user} performed {action} on {resource}")


# In users/permissions.py
def is_professor(user):
    """Check if the given user belongs to the "Professor" group.

    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the user is in the "Professor" group, False otherwise.
    """
    return user.groups.filter(name="Professor").exists()


def is_ta(user):
    """Checks if the given user belongs to the "TA" group.

    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the user is in the "TA" group, False otherwise.
    """
    return user.groups.filter(name="TA").exists()


def is_admin(user):
    """Check if a user has administrative privileges.

    This function determines whether a given user has administrative rights
    by checking if the user is marked as staff or a superuser.

    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the user is a staff member or a superuser, False otherwise.
    """
    return user.is_staff or user.is_superuser


class IsProfessorOrTA(BasePermission):
    """Permission class to check if the user is either a professor or a
    teaching assistant (TA).

    Methods:
        has_permission(request, view):
            Determines if the user has the required permissions to access the view.
            Returns True if the user is authenticated and is either a professor or a TA, otherwise False.

    Attributes:
        Inherits from BasePermission.
    """

    def has_permission(self, request, view):
        """Determines whether the requesting user has the necessary
        permissions.

        This method checks if the user is authenticated and if the user has a role
        of either a professor or a teaching assistant (TA).

        Args:
            request: The HTTP request object containing user information.
            view: The view being accessed (not used in this implementation).

        Returns:
            bool: True if the user is authenticated and is either a professor or a TA,
                  False otherwise.
        """
        return (
            request.user
            and request.user.is_authenticated
            and (is_professor(request.user) or is_ta(request.user))
        )


class IsProfessorOrAdmin(BasePermission):
    """Permission class to grant access only to users who are either professors
    or administrators.

    Methods:
        has_permission(request, view):
            Checks if the user making the request is authenticated and has either professor or admin privileges.

    Args:
        request: The HTTP request object containing user information.
        view: The view being accessed.

    Returns:
        bool: True if the user is authenticated and is either a professor or an admin, False otherwise.
    """

    def has_permission(self, request, view):
        """Determines whether the requesting user has the necessary permissions
        to access a view.

        This method checks if the user is authenticated and if they have either professor
        or admin privileges.

        Args:
            request (HttpRequest): The HTTP request object containing user information.
            view (View): The view being accessed (not used in this implementation).

        Returns:
            bool: True if the user is authenticated and has professor or admin privileges,
            False otherwise.
        """
        return (
            request.user
            and request.user.is_authenticated
            and (is_professor(request.user) or is_admin(request.user))
        )


# for more restrictive views
class IsProfessor(BasePermission):
    """Permission class to check if the requesting user is a professor.

    This permission class ensures that the user making the request is authenticated
    and has the necessary attributes to be identified as a professor.

    Methods:
        has_permission(request, view):
            Returns True if the user is authenticated and is a professor, otherwise False.

    Args:
        request: The HTTP request object containing user information.
        view: The view being accessed.

    Returns:
        bool: True if the user is authenticated and is a professor, False otherwise.
    """

    def has_permission(self, request, view):
        """Determines if the requesting user has the necessary permissions.

        This method checks if the user is authenticated and has the role of a professor.

        Args:
            request (HttpRequest): The HTTP request object containing user information.
            view (View): The view being accessed (not used in this implementation).

        Returns:
            bool: True if the user is authenticated and is a professor, False otherwise.
        """
        return (
            request.user
            and request.user.is_authenticated
            and is_professor(request.user)
        )


class IsAdmin(BasePermission):
    """Permission class to check if the requesting user is an admin.

    This class inherits from `BasePermission` and overrides the `has_permission` method
    to determine whether the user has the required permissions to access a view.

    Methods:
        has_permission(request, view):
            Checks if the user is authenticated and has admin privileges.

    Args:
        request: The HTTP request object containing user information.
        view: The view being accessed.

    Returns:
        bool: True if the user is authenticated and is an admin, False otherwise.
    """

    def has_permission(self, request, view):
        """Determines whether the requesting user has the necessary
        permissions.

        This method checks if the user is authenticated and has administrative privileges.

        Args:
            request (HttpRequest): The HTTP request object containing user information.
            view (View): The view being accessed.

        Returns:
            bool: True if the user is authenticated and is an admin, False otherwise.
        """
        return request.user and request.user.is_authenticated and is_admin(request.user)
