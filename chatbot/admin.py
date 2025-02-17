from django.contrib import admin
from .models import ServiceProvider


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "description", "calendar_url")  # Display these fields in the admin list
    search_fields = ("id", "user__email", "name")  # Enable searching by ID, user email, and name
    list_filter = ("user",)
    ordering = ("id",)
    list_editable = ("name", "description")  # Enable inline editing for these fields
    list_display_links = ("id", "user")  # Prevent name and description from being clickable links
