from django.contrib import admin
from atlas.models import Document

# Register your models here.

class DocumentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Document._meta.fields]

admin.site.register(Document, DocumentAdmin)