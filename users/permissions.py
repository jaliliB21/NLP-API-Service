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


class IsEmailVerified(permissions.BasePermission):
    """
    Custom permission to only allow access to users with a verified email.
    """
    message = 'Please verify your email address to use this feature.'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.is_authenticated and request.user.is_email_verified