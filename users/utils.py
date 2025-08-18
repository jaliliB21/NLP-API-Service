from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .tokens import account_activation_token
from .tasks import send_email_task


def send_verification_email(user):
    """
    Generates a verification token and sends it to the user.
    """
    # Generate the token and user ID for the verification link
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    # Construct the verification URL
    # NOTE: In production, the domain should come from settings or env variables
    frontend_domain = getattr(settings, "FRONTEND_DOMAIN", "http://localhost:8000")
    verification_path = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    verification_url = f"{frontend_domain}{verification_path}"

    # Prepare the email
    subject = 'Activate Your Account'
    message = f'Hi {user.username},\n\nPlease click the link below to verify your email address:\n{verification_url}'
    
    # Key Change: Use .delay() to send the task to the Celery queue
    send_email_task.delay(
        subject=subject, 
        message=message, 
        recipient_list=[user.email]
    )


# This is the helper function for password reset
def send_password_reset_email(user):
    """
    Generates a password reset token and sends it to the user's email.
    """
    # Use Django's default token generator for password reset
    token_generator = PasswordResetTokenGenerator()
    
    # Generate the token and user ID for the link
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    # Construct the full reset URL for the frontend
    # Assumes your frontend has a route like /reset-password/confirm/:uid/:token
    frontend_domain = getattr(settings, "FRONTEND_DOMAIN", "http://localhost:8000")
    reset_path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    reset_url = f"{frontend_domain}{reset_path}"

    # Prepare the email content
    subject = 'Reset Your Password'
    message = (
        f'Hi {user.username},\n\n'
        f'Please click the link below to reset your password:\n'
        f'{reset_url}\n\n'
        f'If you did not request this, please ignore this email.'
    )
    
    # Key Change: Use .delay() to send the task to the Celery queue
    send_email_task.delay(
        subject=subject, 
        message=message, 
        recipient_list=[user.email]
    )
