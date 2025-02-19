from django.db import models
from django.utils import timezone

from atila.utils import random_code, phone_regex


class ServiceClient(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    name = models.CharField(max_length=128)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(max_length=128, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    client = models.ForeignKey(
        ServiceClient,
        on_delete=models.SET_NULL,
        related_name="service_providers",
        null=True
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    cal_com_event_type_id = models.CharField(max_length=128)
    cal_com_api_key = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ServiceBooking(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=random_code)
    client = models.ForeignKey(
        ServiceClient,
        on_delete=models.SET_NULL,
        null=True
    )
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.SET_NULL,
        null=True
    )
    reservation_uid = models.CharField(max_length=280, blank=True, null=True)
    booking_uid = models.CharField(max_length=280, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    deposit_paid = models.BooleanField(default=False)
    deposit_payment_intent_id = models.CharField(max_length=32, blank=True, null=True)

    def get_formatted_start_date(self):
        """Returns the start date formatted in America/Toronto timezone."""
        if not self.start_date:
            return "No date set"

        local_timezone = timezone.get_current_timezone()
        localized_date = timezone.localtime(self.start_date, local_timezone)
        return localized_date.strftime("%A, %B %d, %Y %I:%M %p")

    def __str__(self):
        return f"{self.client} booking with {self.provider} on {self.get_formatted_start_date()}"
