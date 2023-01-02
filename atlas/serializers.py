from rest_framework import serializers

from atlas.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
