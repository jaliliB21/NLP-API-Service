
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated # Added IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView # Base class for login
from rest_framework_simplejwt.tokens import RefreshToken # Added for logout
from django.http import Http404 # For UserDetailView (will be added back later)
from rest_framework_simplejwt.authentication import JWTAuthentication 

from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer, # For login
    TokenBlacklistSerializer,      # For logout
    ChangePasswordSerializer,

)
from .permissions import IsAnonymousOnlyForRegistration 

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    # Apply JWTAuthentication to this view to ensure request.user is populated.
    authentication_classes = [JWTAuthentication] 
    
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Prevent already authenticated users from requesting new tokens.
        if request.user.is_authenticated:
            return Response(
                {'detail': 'You are already logged in.'},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        # Proceed with token generation if not authenticated.
        return super().post(request, *args, **kwargs)


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    Allows unauthenticated users to create a new account.
    """
    permission_classes = [IsAnonymousOnlyForRegistration] # Apply the custom permission here

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {"message": "User registered successfully.", "user_id": user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout (blacklisting the refresh token).
    Requires authentication.
    """
    permission_classes = [IsAuthenticated] # Only authenticated users can logout

    def post(self, request):

        print(f"Request user in UserLogoutView: {request.user}")
        print(f"Is user authenticated in UserLogoutView? {request.user.is_authenticated}")
        
        serializer = TokenBlacklistSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_205_RESET_CONTENT) # 205 indicates content reset (logout successful)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    Requires authentication and current password verification.
    """
    permission_classes = [IsAuthenticated] # Only authenticated users can change password

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user # Get the authenticated user from request.user
            
            # Verify old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": "Old password is not correct."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set the new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Blacklist all refresh tokens for the user to force re-login
            # This invalidates all active sessions for the user.
            try:
                # RefreshToken.for_user(user) generates a token object (not a new token itself)
                # and calling .blacklist() on it blacklists all *outstanding* refresh tokens for that user.
                RefreshToken.for_user(user).blacklist()
            except Exception as e:
                # Log any errors during token blacklisting (e.g., if no tokens exist to blacklist)
                # This should not prevent the password change operation from succeeding.
                print(f"Error blacklisting refresh tokens for user {user.email}: {e}")

            return Response({"message": "Password changed successfully. Please login again."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
