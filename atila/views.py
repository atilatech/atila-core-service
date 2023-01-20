from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from atila.permissions import UserPermission
from atila.serializers import UserSerializer, GroupSerializer, AtilaTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer


class AtilaTokenObtainPairView(TokenObtainPairView):
    serializer_class = AtilaTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

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

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        request_data: {"object_type": "scholarship|contact", "object_id": "<id>",
        "edit_data": {}}
        """
        username = request.data['username']
        password = request.data['password']

        try:
            if username.find('@') != -1:
                user = User.objects.get(email=username)
                username = user.username

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                userprofile = UserProfileSerializer(user.userprofile).data
                refresh = AtilaTokenObtainPairSerializer.get_token(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_profile': userprofile,
                }, status=status.HTTP_202_ACCEPTED)

            else:
                return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist as e:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAdminUser,)
