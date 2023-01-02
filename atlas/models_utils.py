from atlas.serializers import DocumentSerializer


def save_transcribed_document_to_atila_database(video_transcript):
    document = {
        'title': video_transcript['']
    }
    serializer = DocumentSerializer(data=document)
    serializer.is_valid()
    # True
    serializer.save()
    return serializer
