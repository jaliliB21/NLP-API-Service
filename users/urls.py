from django.urls import path
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView, # For login
    UserLogoutView, # For logout
    ChangePasswordView, # For Change Password
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='user_login'), # API for user login
    path('logout/', UserLogoutView.as_view(), name='user_logout'), # API for user logout
    path('change-password/', ChangePasswordView.as_view(), name='change_password'), # New URL for password change
]

