# Generated by Django 4.1.4 on 2025-02-18 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_servicebooking_reservation_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicebooking',
            name='deposit_paid',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='servicebooking',
            name='deposit_payment_intent_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
