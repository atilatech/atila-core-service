from django.contrib import admin
from atlas.models import Document

from atlas.serializers import document_fields


class DocumentAdmin(admin.ModelAdmin):

    document_fields_format_map = {
        'text': 'text_truncated',
        'segments': 'segments_truncated',
    }
    # Create an empty list to store the modified values
    document_fields_display = []

    # Iterate through the document_fields list
    for field in document_fields:
        # Check if the field exists in the document_fields_format_map dictionary
        if field in document_fields_format_map:
            # Append the value from the document_fields_format_map dictionary to the modified_fields list
            document_fields_display.append(document_fields_format_map[field])
        else:
            # Otherwise, append the original field value to the modified_fields list
            document_fields_display.append(field)

    list_display = ['__str__'] + document_fields_display

    def text_truncated(self, obj: Document):
        return obj.text[:280]

    def segments_truncated(self, obj: Document):
        return obj.segments[:2]


admin.site.register(Document, DocumentAdmin)
