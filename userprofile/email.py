from userprofile.models import UserProfile
from atila.email import send_email
from atila.helpers import random_string


def send_verification_code_email(user_profile: UserProfile, create_code=True):
    """
    This code is different from the registration verification. This is meant more as a 2FA type of authentication for
    users whom have already created an account.
    """

    if create_code:
        verification_code = random_string(6, numbers_only=True)
        user_profile.verification_code = verification_code
        user_profile.save()

    subject = f"Atila Verification Code"

    body_data = {
        'username': user_profile.user.username,
        'verification_code': user_profile.verification_code,
    }

    body_html = '''
                    Hey {username}, <br><br>
                    Your verification code is {verification_code}<br><br>
                    Atila Tech
                    '''.format(**body_data)

    email_data = {
        'body': body_html,
        'subject': subject,
        'to_email': user_profile.user.email,
    }

    send_email(email_data, "ses")
