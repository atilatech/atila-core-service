from django.db import models

from atila.utils import random_code
from userprofile.models import UserProfile


class ServiceProvider(models.Model):
    objects = models.Manager()

    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="service_providers")

    name = models.CharField(max_length=128, default="")
    description = models.TextField(blank=True, null=True, default="")

    cal_com_username = models.CharField(max_length=128, default="")
    cal_com_event_type_id = models.CharField(max_length=128, default="")
    cal_com_event_type_slug = models.CharField(max_length=280, default="")
    cal_com_api_key = models.TextField(blank=True, null=True, default="")

    def __str__(self):
        return f"ServiceProvider {self.id} for {self.user}"
