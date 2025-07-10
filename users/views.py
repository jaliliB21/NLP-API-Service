
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
