from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from userprofile.verification import send_verification_code_email, verify_phone_number
from userprofile.models import UserProfile
from userprofile.permissions import UserProfilePermission
from userprofile.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (UserProfilePermission,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['post'], url_path='send-verification-code')
    def send_verification_code(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        send_verification_code_email(username)
        return Response({'message': 'Verification code sent successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-phone-number')
    def verify_phone_number(self, request):
        required_fields = ['phone_number', 'username', 'verification_code']
        missing_fields = [field for field in required_fields if not request.data.get(field)]

        if missing_fields:
            return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        success, message = verify_phone_number(
            request.data['phone_number'],
            request.data['username'],
            request.data['verification_code']
        )

        return Response({"message": message}, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
