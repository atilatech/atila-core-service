from rest_framework import viewsets

from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer
from rest_framework.permissions import IsAdminUser


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
