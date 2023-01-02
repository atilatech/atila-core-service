from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from atlas.models import Document
from atlas.serializers import DocumentSerializer
from atlas.transcribe import transcribe_and_search_video


class SearchView(APIView):

    def get(self, request):
        return self.handle_transcription_request(request.GET)

    def post(self, request):
        return self.handle_transcription_request(request.data)

    @staticmethod
    def handle_transcription_request(request_data):
        url = request_data.get('url')
        query = request_data.get('q')
        if not query:
            return Response({
                'error': "missing 'q' parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        results = transcribe_and_search_video(query, url)

        return Response(results, status=200)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
