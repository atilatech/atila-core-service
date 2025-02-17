from django.contrib import admin
from .models import ServiceProvider, ServiceClient


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "description", "cal_com_event_type_slug", "cal_com_username")
    search_fields = ("id", "user__email", "name")  # Enable searching by ID, user email, and name
    list_filter = ("user",)
    ordering = ("id",)
    list_editable = ("name", "description")  # Enable inline editing for these fields
    list_display_links = ("id", "user")  # Prevent name and description from being clickable links


@admin.register(ServiceClient)
class ServiceClientAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('id', 'name', 'phone_number', 'email', 'date_created')

    # Add search capability for the fields
    search_fields = ('name', 'phone_number', 'email')

    # Filter clients by their creation date
    list_filter = ('date_created',)

    # Allow sorting by fields like name and date_created
    ordering = ('-date_created',)

    # Make phone_number and email fields editable in the list view
    list_editable = ('phone_number', 'email')
