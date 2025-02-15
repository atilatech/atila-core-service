from atila.email import send_email
from atila.helpers import random_string
from userprofile.models import UserProfile


def send_verification_code_email(user_profile: UserProfile, create_code: bool = True):
    """
    Sends a verification code email to the user.

    This is different from registration verification. It acts as a 2FA for users who already have an account.
    """
    if not user_profile or not user_profile.user or not user_profile.user.email:
        raise ValueError("Invalid user profile or missing email address.")

    if create_code:
        verification_code = random_string(6, numbers_only=True)
        user_profile.verification_code = verification_code
        user_profile.save()

    subject = "Atlas Verification Code"
    body_html = f"""
        Hey {user_profile.user.username}, <br><br>
        Your verification code is <strong>{user_profile.verification_code}</strong><br><br>
        Atila
    """

    email_data = {
        'body': body_html,
        'subject': subject,
        'to_email': user_profile.user.email,
    }

    send_email(email_data, "ses")
