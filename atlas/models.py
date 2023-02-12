import hashlib
from typing import Union

from django.db.models import JSONField
from django.db import models
from django.utils import timezone

from atila.utils import random_string, ModelUtils


class DocumentManager(models.Manager):
    def get_by_natural_key(self, url):
        return self.get(url=url)


class Document(models.Model):
    objects = DocumentManager()

    id = models.CharField(max_length=128, primary_key=True, default=random_string)
    url = models.URLField(max_length=500, unique=True)

    title = models.CharField(max_length=500, blank=True, null=True, default="")
    description = models.TextField(max_length=1000, blank=True, null=True, default="")
    text = models.TextField(blank=True, null=True, default="")
    segments = JSONField(default=ModelUtils.empty_list, blank=True, null=True)

    summaries = JSONField(default=ModelUtils.empty_list, blank=True, null=True)

    image = models.URLField(max_length=500, blank=True, null=True, default="")

    views = models.IntegerField(default=0)
    transcription_source = models.CharField(max_length=128, blank=True, null=True, default="")

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title or self.url

    def save(self, *args, **kwargs):
        self.url = self.url.rstrip("/")
        if self._state.adding:
            self.id = self.url_to_object_id(self.url)

        super().save(*args, **kwargs)

    @staticmethod
    def url_to_object_id(url: Union[models.URLField, str]):
        url = url.rstrip("/")
        hash_object = hashlib.new('sha256')
        hash_object.update(url.encode())
        object_id = hash_object.hexdigest()
        return object_id

