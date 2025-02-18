import pytz
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

    objects = models.Manager()

    def __str__(self):
        return self.name


class ServiceBooking(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    client = models.ForeignKey(to=ServiceClient, on_delete=models.deletion.SET_NULL, null=True)
    provider = models.ForeignKey(to=ServiceProvider, on_delete=models.deletion.SET_NULL, null=True)

    reservation_uid = models.CharField(max_length=280, blank=True, null=True)
    booking_uid = models.CharField(max_length=280, blank=True, null=True)

    start_date = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(default=timezone.now)

    deposit_paid = models.BooleanField(default=False)
    deposit_payment_intent_id = models.CharField(max_length=32, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        if self.start_date:
            # Set timezone to America/Toronto
            toronto_tz = pytz.timezone('America/Toronto')

            # Localize the datetime to America/Toronto timezone
            localized_start_date = self.start_date.astimezone(toronto_tz)

            # Format the date in the specified format
            formatted_date = localized_start_date.strftime("%A, %B %d, %Y %I:%M %p")
        else:
            formatted_date = "No date set"

        return f"{self.client} booking with {self.provider} on {formatted_date}"
