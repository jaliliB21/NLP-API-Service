from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .tokens import account_activation_token


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
    
    # Send the email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL, # Use default from email from settings
        [user.email],
        fail_silently=False,
    )