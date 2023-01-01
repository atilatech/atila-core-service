import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from atlas.transcribe import transcribe_and_search_video

class SearchView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            url = request.GET.get('url')
            query = request.GET.get('q')
        elif request.method == 'POST':
            post_body = json.loads(request.body)
            url = post_body.get('url')
            query = post_body.get('q')

        print('request.body', request.body)
        print('post_body', post_body)
        transcribed_video = transcribe_and_search_video(query, url)

        return JsonResponse({"results": transcribed_video}, status=200)

