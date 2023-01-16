from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from atlas.models import Document
from atlas.serializers import DocumentSerializer, DocumentPreviewSerializer
from atlas.transcribe import transcribe_and_search_video
from pytube import YouTube

from userprofile.models import UserProfile

MAX_VIDEO_LENGTH = 900  # TODO: Fix, can't transcribe videos longer than 900 seconds due to timeout errors.


class SearchView(APIView):

    def get(self, request):
        return self.handle_transcription_request(request)

    def post(self, request):
        return self.handle_transcription_request(request)

    @staticmethod
    def handle_transcription_request(request):
        if request.method == 'GET':
            request_data = request.GET
        else:
            request_data = request.data

        url = request_data.get('url')
        query = request_data.get('q')
        video = None
        if not query:
            return Response({
                'error': "missing 'q' parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        if url:
            video = YouTube(url)

        results = transcribe_and_search_video(query, url, video)

        user_profile = UserProfile.get_user_profile_from_request(request)

        if user_profile:
            user_profile.atlas_transcriptions += 1
            user_profile.save()

        return Response(results, status=200)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = DocumentPreviewSerializer
        return super().list(request, *args, **kwargs)
