from django.contrib.auth.models import User
from rest_framework import serializers

from atlas.models import Document
from userprofile.models import UserProfile

userprofile_fields = ['id', 'user', 'atlas_searches', 'atlas_transcriptions', 'date_created', 'date_modified']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = userprofile_fields
