# Generated by Django 4.1.4 on 2025-02-17 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_remove_serviceprovider_bio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='name',
            field=models.CharField(default='', max_length=128),
        ),
    ]
