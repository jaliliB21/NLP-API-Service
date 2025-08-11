
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated # Added IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView # Base class for login
from rest_framework_simplejwt.tokens import RefreshToken # Added for logout
from django.http import Http404 # For UserDetailView (will be added back later)
from rest_framework_simplejwt.authentication import JWTAuthentication 
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer, # For login
    TokenBlacklistSerializer,      # For logout
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer,

)

from .tokens import account_activation_token
from .permissions import IsAnonymousOnlyForRegistration, IsAnonymousOnly
from .utils import send_verification_email, send_password_reset_email

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
    Allows unauthenticated users to create a new account and logs them in automatically.
    """
    # Your original, correct permission class is back.
    permission_classes = [IsAnonymousOnlyForRegistration]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        
        # We use your original, correct structure for validation.
        if serializer.is_valid(raise_exception=True):
            # The serializer's create method handles user creation
            user = serializer.save()

            # --- Auto-login and email verification logic starts here ---

            # Send a verification email to the new user
            send_verification_email(user)

            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            # Prepare the response data including tokens for auto-login
            response_data = {
                'detail': 'User registered successfully. Please check your email to verify your account.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    "full_name": user.full_name,
                    'is_email_verified': user.is_email_verified,
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # If the serializer is not valid, return the errors.
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


class SendVerificationEmailView(APIView):
    """
    An endpoint for logged-in but unverified users to request a verification email.
    The actual email sending logic is handled by a helper function.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.is_email_verified:
            return Response(
                {'detail': 'Your email address has already been verified.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call the helper function to send the email
        send_verification_email(user)

        return Response(
            {'detail': 'A verification email has been sent to your email address.'},
            status=status.HTTP_200_OK
        )


class VerifyEmailView(APIView):
    """
    An endpoint to handle email verification link clicks.
    """
    # This view should be accessible to anyone with the link, so we allow any access.
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            # Decode the user id from the base64 encoded string
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if user exists and the token is valid
        if user is not None and account_activation_token.check_token(user, token):
            
            # Check if the email is already verified
            if user.is_email_verified:
                # You might want to redirect to a frontend page saying "already verified"
                return Response(
                    {'detail': 'Your email address has already been verified.'}, 
                    status=status.HTTP_200_OK
                )

            # Activate the user's email
            user.is_email_verified = True
            user.save()

            # You can redirect to a success page on your frontend
            return Response(
                {'detail': 'Your email has been successfully verified! You can now log in.'}, 
                status=status.HTTP_200_OK
            )
        else:
            # Invalid link
            # You can redirect to a failure page on your frontend
            return Response(
                {'detail': 'The activation link is invalid or has expired.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class RequestPasswordResetEmailView(APIView):
    """
    An endpoint for unauthenticated users to request a password reset email.
    """
    permission_classes = [IsAnonymousOnly]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Send the password reset email using our helper function
        send_password_reset_email(user)

        return Response(
            {"detail": "If an account with this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    """
    An endpoint to handle the password reset confirmation and set a new password.
    """
    permission_classes = [IsAnonymousOnly]

    def post(self, request, uidb64, token, *args, **kwargs):
        # Pass context containing uid and token from the URL to the serializer
        context = {'uidb64': uidb64, 'token': token}
        serializer = SetNewPasswordSerializer(data=request.data, context=context)
        
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['password']

        # Set the new password
        user.set_password(new_password)
        user.save()

        # --- code for auto-login starts here ---

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        # Prepare the response data including tokens
        response_data = {
            'detail': 'Your password has been reset successfully. You are now logged in.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                    'id': user.id,
                    'email': user.email,
                    "full_name": user.full_name,
                }
        }

        return Response(response_data, status=status.HTTP_200_OK)