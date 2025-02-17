from django.db import models

from atila.utils import random_string
from userprofile.models import UserProfile


class ServiceProvider(models.Model):
    objects = models.Manager()

    id = models.CharField(max_length=32, primary_key=True, default=random_string)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="service_providers")

    name = models.CharField(max_length=128, default="")
    description = models.TextField(blank=True, null=True, default="")
    calendar_url = models.URLField(blank=True, max_length=1000)

    def __str__(self):
        return f"ServiceProvider {self.id} for {self.user}"
