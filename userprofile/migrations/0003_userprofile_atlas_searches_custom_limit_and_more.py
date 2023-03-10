# Generated by Django 4.1.4 on 2023-01-19 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_alter_userprofile_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='atlas_searches_custom_limit',
            field=models.IntegerField(default=0, help_text='Allow certain users to bypass the MAX_REGISTERED_FREE_SEARCHES.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ]
