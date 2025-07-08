from rest_framework import permissions

class IsAnonymousOnly(permissions.BasePermission):
    """
    Custom permission to only allow access to unauthenticated users.
    """
    message = 'You are already authenticated. You cannot register again.' # Custom error message

    def has_permission(self, request, view):
        # Allow access only if the user is NOT authenticated (is_authenticated is False)
        return not request.user.is_authenticated
        