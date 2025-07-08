from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from uuid import uuid4 # For generating unique username if needed

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