from django.contrib import admin
from .models import ServiceProvider, ServiceClient, ServiceBooking


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "name", "description", "cal_com_event_type_id")
    search_fields = ("id", "client__email", "name")  # Enable searching by ID, client email, and name
    list_filter = ("client",)
    ordering = ("id",)
    list_editable = ("name", "description")  # Enable inline editing for these fields
    list_display_links = ("id", "client")  # Prevent name and description from being clickable links


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


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('id', 'client', 'provider', 'start_date', 'date_created')

    # Add search capability for related client and provider names
    search_fields = ('client__name', 'client__phone_number', 'provider__name')

    # Filter bookings by start date and creation date
    list_filter = ('start_date', 'date_created')

    # Allow sorting by start_date and date_created
    ordering = ('-date_created',)

    # Make start_date editable in the list view
    list_editable = ('start_date',)
