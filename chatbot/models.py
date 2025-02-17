from django.db import models

from atila.utils import random_string


# Create your models here.
class ServiceProvider(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_string)
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    description = models.TextField(max_length=400, blank=True, null=True)
    bio = models.TextField(blank=True, null=True, default="")
    mentorship_topics = models.TextField(blank=True, null=True, default="")
    bio_recording_url = models.URLField(blank=True, max_length=1000)