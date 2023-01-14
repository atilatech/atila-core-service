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
        if not query:
            return Response({
                'error': "missing 'q' parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        if url:
            video = YouTube(url)
            if video.length > MAX_VIDEO_LENGTH:
                return Response({
                    'error': f"Atlas can currently only transcribe videos less than {int(MAX_VIDEO_LENGTH / 60)} "
                             f"minutes long. "
                             f"Please try again with a shorter video. "
                             f"Sorry for the inconvenience, we're working on increasing this limit. "
                             f"The video '{video.title}' is about {int(video.length / 60)} minutes long. "
                }, status=status.HTTP_400_BAD_REQUEST)

        results = transcribe_and_search_video(query, url)

        user_profile = UserProfile.get_user_profile_from_request(request_data)

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
