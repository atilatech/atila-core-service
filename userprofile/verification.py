from django.core.exceptions import ObjectDoesNotExist
from atila.email import send_email
from atila.utils import random_string
from userprofile.models import UserProfile


def send_verification_code_email(username: str, create_code: bool = True):
    """
    Sends a verification code email to the user for 2FA.
    """
    try:
        user_profile = UserProfile.objects.get(user__username=username)
        if not user_profile.user.email:
            raise ValueError("Missing email address.")
    except ObjectDoesNotExist:
        return False, "User profile not found."

    if create_code:
        user_profile.verification_code = random_string(6)
        user_profile.save()

    send_email({
        'body': f"Hey {user_profile.user.username}, <br><br>"
                f"Your verification code is <strong>{user_profile.verification_code}</strong><br><br>Atila",
        'subject': "Atlas Verification Code",
        'to_email': user_profile.user.email,
    }, "ses")
    return True, "Verification code sent successfully."


def verify_phone_number(phone_number: str, username: str, verification_code: str):
    try:
        user_profile = UserProfile.objects.get(user__username=username)
        if verification_code == user_profile.verification_code:
            user_profile.phone_number = phone_number
            user_profile.save()
            return True, "Linked phone number to user"
        return False, "Error: Invalid verification code."
    except ObjectDoesNotExist:
        return False, "Error: User does not exist."
