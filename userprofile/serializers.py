from rest_framework import serializers

from atila.serializers import UserSerializer
from userprofile.models import UserProfile

userprofile_fields = ['id', 'user', 'atlas_searches', 'atlas_transcriptions', 'date_created', 'date_modified']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = userprofile_fields
