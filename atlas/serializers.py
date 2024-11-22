from rest_framework import serializers

from atlas.models import Document

document_fields_preview = ['id', 'url', 'title', 'description', 'image', 'views', 'transcription_source',
                           'date_created', 'date_modified']
document_fields = document_fields_preview + ['text', 'segments', 'summaries']

credits_code_serializer_fields = ['id', 'code', 'used_by', 'atlas_credits', 'date_created', 'date_modified']


class DocumentPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = document_fields_preview


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = document_fields
