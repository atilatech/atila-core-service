from django.db import models
from django.utils import timezone

from atila.utils import random_code, phone_regex
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

    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ServiceClient(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    name = models.CharField(max_length=128)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=128, blank=True, null=True)

    date_created = models.DateTimeField(default=timezone.now)

    objects = models.Manager()  # Default manager

    def __str__(self):
        return f"{self.name}"
