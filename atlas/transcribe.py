import time

from atlas.encode import upload_transcripts_to_vector_db, query_model, does_video_exist_in_pinecone
from atlas.models import Document
from atlas.models_utils import save_transcribed_video_to_atila_database
from atlas.utils import convert_seconds_to_string, parse_video_id, send_transcription_request


def transcribe_and_search_video(query, url=None, verbose=True):
    t0 = time.time()
    video_id = parse_video_id(url)
    video_with_transcript = {}
    # Transcribe the video if a url has been provided and either the video transcript
    # hasn't been uploaded to our database or the video vectors haven't been uploaded to pinecone.

    print('not Document.objects.filter(url=f"https://www.youtube.com?v={video_id}").exists()',
          not Document.objects.filter(url=f"https://www.youtube.com?v={video_id}").exists()
          )
    if url and (not Document.objects.filter(url=f"https://www.youtube.com?v={video_id}").exists()
                or not does_video_exist_in_pinecone(url)):
        video_with_transcript = send_transcription_request(url)
        save_transcribed_video_to_atila_database(video_with_transcript)
        upload_transcripts_to_vector_db(video_with_transcript['encoded_segments'])
    else:
        print(f'Skipping transcribing and embedding. ')
        if not url:
            print('No URL provided, searching all videos')
        else:
            print(f'Video already exists:{url}')
    results = query_model(query, video_id)
    t1 = time.time()
    total = t1 - t0
    if verbose:
        video_length = f"{convert_seconds_to_string(results['matches'][0]['metadata']['length'])} " \
                       "long video" \
            if len(results['matches']) > 0 else 'no video found'
        print(f'Transcribed and searched {video_length} in {total} seconds')
    return {'results': results,
            'video': {**video_with_transcript} if video_with_transcript else None
            }
