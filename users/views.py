from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny # Remove this
from .permissions import IsAnonymousOnly # Import your custom permission

from .serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    Allows unauthenticated users to create a new account.
    """
    permission_classes = [IsAnonymousOnly] # Apply the custom permission here

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {"message": "User registered successfully.", "user_id": user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
