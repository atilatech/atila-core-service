from django.contrib import admin

from userprofile.models import UserProfile
from userprofile.serializers import userprofile_fields


class UserProfileAdmin(admin.ModelAdmin):

    list_display = ['__str__'] + userprofile_fields


admin.site.register(UserProfile, UserProfileAdmin)
