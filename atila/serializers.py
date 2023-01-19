from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AtilaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Use a custom TokenObtainPairSerializer so that userprofile_id is included in the request
    to promote using the randomly generated userprofile_id instead of the sequential user_id.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['userprofile_id'] = user.userprofile.id

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
