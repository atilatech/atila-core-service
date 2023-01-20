from rest_framework import viewsets

from userprofile.models import UserProfile
from userprofile.permissions import UserProfilePermission
from userprofile.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (UserProfilePermission,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
