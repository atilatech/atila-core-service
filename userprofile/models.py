from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.request import Request

from atila.utils import random_string


# Create your models here.
class UserProfile(models.Model):  # add this class and the following fields

    objects = models.Manager()

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.CharField(max_length=128, primary_key=True, default=random_string)

    atlas_searches = models.IntegerField(default=0)
    atlas_transcriptions = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)

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
    def get_user_profile_from_request(cls, request: Request, use_api_key_credit_public_key=False):
        """
        A helper method to get a user_profile from a request object.
        Checks the user is authenticated and that the user profile for that user exists.
        If no authentication is provided and use_api_key_credit_public_key is set to true then check
        the user credentials using api public key.
        :param use_api_key_credit_public_key:
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
