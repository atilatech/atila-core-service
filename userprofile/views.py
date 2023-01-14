from django.shortcuts import render
from rest_framework import viewsets

from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
