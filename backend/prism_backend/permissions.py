from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """Custom permission that denies access to authenticated users
    Use cases
    - Not allowing authenticated users to sign in unless they've logged out first
    - Not allowing authenticated users to sign in with OAuth unless they've logged out first
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated
