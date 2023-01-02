from rest_framework import serializers

from atlas.models import Document

document_fields = ['id', 'url', 'title', 'description', 'text', 'segments',
                   'image', 'date_created', 'date_modified']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = document_fields
