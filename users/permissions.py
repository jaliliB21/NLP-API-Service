# users/permissions.py

from rest_framework import permissions

class IsAnonymousOnlyForRegistration(permissions.BasePermission):
    """
    Custom permission to only allow access to unauthenticated users for registration.
    Returns a specific message for authenticated users.
    """
    message = 'You are already authenticated. You cannot register again.'

    def has_permission(self, request, view):

        return not request.user.is_authenticated
