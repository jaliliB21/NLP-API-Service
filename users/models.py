from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Overriding the default email field from AbstractUser to make it unique
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name='email address')
    
    # Adding a single field for full name as requested
    full_name = models.CharField(max_length=255, blank=True, verbose_name='full name')

    # Fields for usage limits and premium plan
    is_pro = models.BooleanField(default=False, verbose_name="Is Pro User")
    free_analysis_count = models.IntegerField(default=10, verbose_name="Free Analysis/Summarization Count") # Default 10 free uses

    # Let's go with the more common API approach: Login with `email`.
    USERNAME_FIELD = 'email' # Users will log in using their email
    REQUIRED_FIELDS = ['username'] # `username` is still required by AbstractUser but not used for login.
                                   # We will handle generating or making it optional in serializers for new users.

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        # Choose how user objects are represented (e.g., in admin panel)
        return self.email if self.email else self.username