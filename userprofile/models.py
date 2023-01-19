from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.request import Request

from atila.settings import ATILA_STAGE
from atila.utils import random_string
from userprofile.constants import RESERVED_USERNAMES


# Create your models here.
class UserProfile(models.Model):  # add this class and the following fields

    objects = models.Manager()

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.CharField(max_length=128, primary_key=True, default=random_string)

    atlas_searches = models.IntegerField(default=0)
    atlas_searches_custom_limit = models.IntegerField(default=0,
                                                      help_text='Allow certain users to bypass the '
                                                                'MAX_REGISTERED_FREE_SEARCHES.')
    atlas_transcriptions = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)

    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created', ]

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)  # add this
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)  # add this
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

    @classmethod
    def get_user_profile_from_request(cls, request: Request):
        """
        A helper method to get a user_profile from a request object.
        Checks the user is authenticated and that the user profile for that user exists.
        If no authentication is provided and use_api_key_credit_public_key is set to true then check
        the user credentials using api public key.
        :param request:
        :return:
        """
        if not request.user.is_authenticated:
            return None
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def verify_user_creation(username, email, password):
        """
        Validate creating a user object. Returns a dict with an 'error' key that describes the problem
        if the user is not valid.
        """
        if not email:
            return {
                'error': 'email cannot be blank'
            }

        if not password:
            return {
                'error': 'password cannot be blank'
            }

        if not username:
            return {
                'error': 'username cannot be blank'
            }

        if ATILA_STAGE == "prod" and username == password:
            return {
                'error': 'username and password cannot be the same'
            }
        if username in RESERVED_USERNAMES:
            return {
                'error': 'Username is reserved'
            }
        if '@' in username:
            return {
                'error': "Username cannot contain '@' symbol."
            }

        # Check if the username is already taken
        if User.objects.filter(username__iexact=username).exists():
            return {
                'error': 'Username is already taken',
            }

        # Check if email is already associated with another account
        if User.objects.filter(email__iexact=email).exists():
            return {
                'error': 'Email is already taken.'
            }

        return {
            'success': 'No errors found'
        }
