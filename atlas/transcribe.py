import time

from atlas.encode import upload_transcripts_to_vector_db, query_model, does_video_exist
from atlas.utils import convert_seconds_to_string, parse_video_id, send_transcription_request




def transcribe_and_search_video(query, url = None, verbose=True):
    t0 = time.time()
    video_id = parse_video_id(url)
    if url and not does_video_exist(url):
        video_with_transcript = send_transcription_request(url)
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
    return results