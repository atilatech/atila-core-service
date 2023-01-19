from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from atila.serializers import UserSerializer, GroupSerializer, AtilaTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from userprofile.models import UserProfile


class AtilaTokenObtainPairView(TokenObtainPairView):
    serializer_class = AtilaTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        user_data = request.data['user']

        username = user_data['username']
        password = user_data['password']
        email = user_data['email']

        validate_user_response = UserProfile.verify_user_creation(username, email, password)

        if 'error' in validate_user_response:
            return Response(validate_user_response, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username, email, password)
        user.save()

        refresh = AtilaTokenObtainPairSerializer.get_token(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAdminUser,)
