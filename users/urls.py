from django.urls import path
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView, # For login
    UserLogoutView, # For logout
    ChangePasswordView, # For Change Password
    SendVerificationEmailView,
    VerifyEmailView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='user_login'), # API for user login
    path('logout/', UserLogoutView.as_view(), name='user_logout'), # API for user logout
    path('change-password/', ChangePasswordView.as_view(), name='change_password'), # New URL for password change

    # --- New URLs for Email Verification ---
    path('send-verification-email/', SendVerificationEmailView.as_view(), name='send_verification_email'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
]



