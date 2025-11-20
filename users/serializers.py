from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from uuid import uuid4 # For generating unique username if needed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # Added for login
from rest_framework_simplejwt.tokens import RefreshToken # Added for Logout

User = get_user_model() # Always use get_user_model() for CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'password', 'password2']
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True}, # Make username optional in API input
            'email': {'required': True},
            'full_name': {'required': False, 'allow_blank': True}
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # If username is not provided, generate a unique one
        if not attrs.get('username') or attrs['username'].strip() == '':
            # Generate a unique username based on email prefix and a short UUID
            email_prefix = attrs['email'].split('@')[0]
            # Ensure uniqueness: if email prefix is short, use more of UUID.
            # For simplicity, use a portion of UUID.
            attrs['username'] = f"{email_prefix[:20]}_{uuid4().hex[:8]}" 
            # Ensure the generated username is unique in the database
            if User.objects.filter(username=attrs['username']).exists():
                raise serializers.ValidationError({"username": "Generated username already exists. Please try again or provide one manually."})

        return attrs

    def create(self, validated_data):
        # Pop password2 as it's not a model field
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''), # Use .get for optional fields
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT TokenObtainPairSerializer to allow login with email.
    """
    def validate(self, attrs):
        # Use email for authentication instead of username
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        # Temporarily set username to email for the default validation to work
        # The default TokenObtainPairSerializer expects a 'username' field.
        # We map 'email' to 'username' for the superclass's validation.
        attrs['username'] = email 
        
        # Call the superclass's validate method
        data = super().validate(attrs)

        # Optionally, remove the temporary 'username' from the response data if not needed
        # This prevents 'username' from appearing in the login response if it's not the primary login field
        if 'username' in data:
            del data['username'] 

        # Add custom claims to the token here if not already done in settings.py
        # Or customize the data returned in the response
        user = self.user # The authenticated user is available via self.user after super().validate
        data['email'] = user.email
        data['full_name'] = user.full_name
        data['is_staff'] = user.is_staff # Useful for front-end to know if user is admin

        return data

class TokenBlacklistSerializer(serializers.Serializer):
    """
    Serializer for blacklisting the refresh token on logout.
    """
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            # Attempt to get the RefreshToken object
            token = RefreshToken(attrs["refresh"])
            token.blacklist() # Blacklist the token
        except Exception as e:
            raise serializers.ValidationError({"detail": "Invalid or expired refresh token."})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    Requires old password, new password, and new password confirmation.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Check if new passwords match
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        # Check if a user with this email exists and is active.
        try:
            user = User.objects.get(email=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active user found with this email address.")
        
        # You can also check if their email is verified, which is good practice
        if not user.is_email_verified:
            raise serializers.ValidationError("Your email address is not verified.")
            
        return value


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for confirming the password reset and setting a new password.
    Receives uidb64 and token via context from the view.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Get token and uid from context passed by the view
        uidb64 = self.context.get('uidb64')
        token = self.context.get('token')

        try:
            # Decode the user id
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'detail': 'Invalid user ID.'})

        # Use Django's default token generator for password reset
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({'detail': 'The reset link is invalid or has expired.'})

        # Attach the user object to the validated data to use in the view
        attrs['user'] = user
        return attrs


# Serializer for User Profile 
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating user profile information.
    """
    date_joined = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = User
        # Fields to display in the API
        fields = [
            'username', 
            'email', 
            'full_name', 
            'is_email_verified', 
            'date_joined'
        ]

        # Fields that can be read but not edited by the user
        read_only_fields = ['email', 'is_email_verified', 'date_joined']
