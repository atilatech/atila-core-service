# Generated by Django 4.1.4 on 2025-02-18 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0010_servicebooking'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicebooking',
            name='reservation_uid',
            field=models.CharField(blank=True, max_length=280, null=True),
        ),
    ]
