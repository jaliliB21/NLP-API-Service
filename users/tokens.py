from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    This class generates a one-time use token for account activation.
    It uses the user's primary key, timestamp, and email verification status
    to create a unique hash.
    """
    def _make_hash_value(self, user, timestamp):
        # This method creates the unique hash value for the token.
        # We include the user's pk, timestamp, and their email verification status
        # to ensure the token is invalidated once the email is verified.
         return (
            str(user.pk) + 
            str(timestamp) +
            str(user.is_email_verified)
        )


# Create an instance of the generator to use in our views
account_activation_token = AccountActivationTokenGenerator()