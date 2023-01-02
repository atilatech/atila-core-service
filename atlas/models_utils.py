from atlas.serializers import DocumentSerializer

YOUTUBE_URL_PREFIX = "https://www.youtube.com/watch"


def save_transcribed_video_to_atila_database(video_data):
    document = {
        'url': f"{YOUTUBE_URL_PREFIX}?v={video_data['video']['id']}",
        'title': video_data['video']['title'],
        'description': video_data['transcript']['segments'][0]['text']
        if len(video_data['transcript']['segments']) > 0
        else '',
        'image': video_data['video']['thumbnail'],
        'text': video_data['transcript']['text'],
        'segments': video_data['transcript']['segments'],
    }
    serializer = DocumentSerializer(data=document)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        print(f"Saved: {document['title']} to Atila database")
    return serializer
