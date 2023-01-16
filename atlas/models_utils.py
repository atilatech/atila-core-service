from atlas.models import Document
from atlas.serializers import DocumentSerializer

YOUTUBE_URL_PREFIX = "https://www.youtube.com/watch"


def save_transcribed_video_to_atila_database(video_data):
    document_dict = {
        'url': f"{YOUTUBE_URL_PREFIX}?v={video_data['video']['id']}",
        'title': video_data['video']['title'],
        'description': video_data['transcript']['segments'][0]['text']
        if len(video_data['transcript']['segments']) > 0
        else '',
        'image': video_data['video']['thumbnail'],
        'text': video_data['transcript']['text'],
        'views': video_data['video']['views'],
        'transcription_source': video_data['transcript']['transcription_source'],
        'segments': video_data['transcript']['segments'],
    }
    document = Document(**document_dict)
    document.save()
    print(f"Saved: {document.title} to Atila database")
    return document
