from requests import HTTPError
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from atlas.constants import MAX_GUEST_SEARCHES, GUEST_SEARCH_LIMIT_REACHED, MAX_REGISTERED_FREE_SEARCHES, \
    REGISTERED_FREE_SEARCH_LIMIT_REACHED
from atlas.models import Document
from atlas.serializers import DocumentSerializer, DocumentPreviewSerializer
from atlas.summarize import summarize_video
from atlas.transcribe import transcribe_and_search_video
from pytube import YouTube

from atlas.transcribe_collection import calculate_cost_for_transcribing_a_collection
from atlas.utils import send_ai_request
from userprofile.models import UserProfile

MAX_VIDEO_LENGTH = 900  # TODO: Fix, can't transcribe videos longer than 900 seconds due to timeout errors.


class SearchView(APIView):

    def get(self, request):
        return self.handle_transcription_request(request)

    def post(self, request):
        return self.handle_transcription_request(request)

    @staticmethod
    @api_view(['POST'])
    def calculate_cost(request):
        url = request.data.get("url")
        phone = request.data.get("phone")
        email = request.data.get("email")
        metadata = {
            'phone': phone,
            'email': email,
        }
        result = calculate_cost_for_transcribing_a_collection(url, metadata)
        return Response(result)

    def handle_transcription_request(self, request):
        if request.method == 'GET':
            request_data = request.GET
        else:
            request_data = request.data

        url = request_data.get('url')
        query = request_data.get('q')

        question = request_data.get('question')
        summarize = request_data.get('summarize') or not query and not question
        print('request_data', request_data)
        try:
            if summarize:
                return self.handle_summarization_request(url)

            user_can_make_atlas_request = self.validate_if_user_can_make_atlas_request(request)

            print('user_can_make_atlas_request', user_can_make_atlas_request)
            if 'error' in user_can_make_atlas_request:
                return Response(user_can_make_atlas_request, status=status.HTTP_400_BAD_REQUEST)

            if question:
                return self.handle_question_answer_request(request_data)

            video = None

            if url:
                video = YouTube(url)

            results = transcribe_and_search_video(query, url, video)

            atlas_searches = self.update_atlas_searches_count(request)

            return Response({**results, 'atlas_searches': atlas_searches}, status=200)

        except HTTPError as e:
            return Response({"error": str(e)}, status=400)

    @staticmethod
    def handle_summarization_request(url):
        """
        Decided to handle transcription and summarization in 2 separate request cycles to manage
        separation of concerns and allow both to operate independently.
        """

        if not url:
            return Response({
                'error': "missing 'url'"
            }, status=status.HTTP_400_BAD_REQUEST)

        results = summarize_video(url)

        return Response({**results}, status=400 if "error" in results else 200)

    @staticmethod
    def handle_question_answer_request(request_data):

        question = request_data.get('question')
        context = request_data.get('context')

        results = send_ai_request({'question': question, 'context': context}, 'openai')

        return Response({"results": results}, status=200)

    @staticmethod
    def validate_if_user_can_make_atlas_request(request):
        """
        1. If user is not logged in, they can only make 10 searches.
        2. If they are logged in but a free account they can make 20 searches.
        3. If they are logged in and have a premium account they can make unlimited searches every month.

        ">=" is used because the check happens at the beginning so if the current searches made is 10,
        then this means this is actually the 11th request.
        """
        # Number of visits to this view, as counted in the session variable.

        if not request.user.is_authenticated:
            atlas_searches = request.session.get('atlas_searches', 0)
            if atlas_searches >= MAX_GUEST_SEARCHES:
                return {
                    'error': f"You have passed the {MAX_GUEST_SEARCHES} search limit for guest users. "
                             f"Please make a free account to make more searches",
                    'error_code': GUEST_SEARCH_LIMIT_REACHED,
                    'atlas_searches': atlas_searches,
                }
        else:
            user_profile = UserProfile.get_user_profile_from_request(request)
            atlas_searches = user_profile.atlas_searches
            if user_profile.is_premium:  # premium users have no search limit
                return {
                    'success': "Premium users have no search limit.",
                    'atlas_searches': atlas_searches,
                }
            if atlas_searches >= MAX_REGISTERED_FREE_SEARCHES \
                    and atlas_searches > user_profile.atlas_searches_custom_limit:
                return {
                    'error': f"You have passed the {MAX_REGISTERED_FREE_SEARCHES} search limit for free users. "
                             f"Please upgrade your account to make more searches",
                    'error_code': REGISTERED_FREE_SEARCH_LIMIT_REACHED,
                    'atlas_searches': atlas_searches,
                }
        return {
            'success': "User is within search limit",
            'atlas_searches': atlas_searches,
        }

    @staticmethod
    def update_atlas_searches_count(request):

        user_profile = UserProfile.get_user_profile_from_request(request)

        if user_profile:
            user_profile.atlas_searches += 1
            user_profile.save()
            atlas_searches = user_profile.atlas_searches
        else:
            request.session['atlas_searches'] = request.session.get('atlas_searches', 0) + 1
            atlas_searches = request.session['atlas_searches']

        return atlas_searches


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = DocumentPreviewSerializer
        return super().list(request, *args, **kwargs)
