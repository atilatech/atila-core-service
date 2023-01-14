from rest_framework import serializers

from atlas.models import Document

document_fields_preview = ['id', 'url', 'title', 'description', 'image', 'date_created', 'date_modified']
document_fields = document_fields_preview + ['text', 'segments']


class DocumentPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = document_fields_preview


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = document_fields
