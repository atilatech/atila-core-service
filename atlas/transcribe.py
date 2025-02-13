from typing import Union

import pytube
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript
from youtube_transcript_api.formatters import TextFormatter, JSONFormatter

from atlas.encode import upload_transcripts_to_vector_db, query_model, does_video_exist_in_pinecone
from atlas.models import Document
from atlas.models_utils import save_transcribed_video_to_atila_database, YOUTUBE_URL_PREFIX
from atlas.serializers import DocumentSerializer
from atlas.utils import convert_seconds_to_string, parse_video_id, send_ai_request

pytube.innertube._default_clients['ANDROID'] = pytube.innertube._default_clients['WEB']

import time


def transcribe_and_search_video(query, url=None, verbose=True, use_ai=True):
    t0 = time.time()
    video_id = parse_video_id(url)

    # Check if the video exists in the database or Pinecone
    document_filter = Document.objects.filter(url=f"{YOUTUBE_URL_PREFIX}?v={video_id}")

    # If no video exists or needs to be transcribed
    if url and (not document_filter.exists() or not does_video_exist_in_pinecone(url)):
        try:
            if use_ai:
                # Use AI-based transcription when use_ai is True
                video_with_transcript = get_transcript_from_youtube(url)
                print('Using YouTube Transcript')
                video_with_transcript['encoded_segments'] = send_ai_request(
                    {"query": video_with_transcript['transcript']['segments']}
                )['encoded_segments']
            else:
                # Fallback to Whisper transcription if AI is disabled
                print('AI transcription disabled. Using Whisper.')
                video_with_transcript = send_ai_request({"video_url": url})
                if 'transcription_source' not in video_with_transcript.get('transcript'):
                    video_with_transcript['transcript']['transcription_source'] = 'whisper'
        except CouldNotRetrieveTranscript as e:
            print('Could not retrieve transcript from YouTube. Switching to transcription with Whisper.', e)
            video_with_transcript = send_ai_request({"video_url": url})
            if 'transcription_source' not in video_with_transcript.get('transcript'):
                video_with_transcript['transcript']['transcription_source'] = 'whisper'

        # Save transcript if not already in the database
        if not document_filter.exists():
            save_transcribed_video_to_atila_database(video_with_transcript)

        # Upload to Pinecone if necessary
        if not does_video_exist_in_pinecone(url):
            upload_transcripts_to_vector_db(video_with_transcript['encoded_segments'])
    else:
        print(f'Skipping transcription and embedding. Video already exists or no URL provided.')
        if not url:
            print('No URL provided, searching all videos.')
        else:
            print(f'Video already exists: {url}')

    # Search for the video if a query is provided
    results = {'matches': []}
    if query:
        results = query_model(query, video_id)
        t1 = time.time()
        total_time = t1 - t0
        if verbose:
            video_length = f"{convert_seconds_to_string(results['matches'][0]['metadata']['length'])} long video" \
                if len(results['matches']) > 0 else 'no video found'
            print(f'Transcribed and searched {video_length} in {total_time} seconds')

    # Fetch video details if it exists in the database
    video = None
    if document_filter.exists():
        video = document_filter.get()
        video = DocumentSerializer(video).data

    return {'results': results, 'video': video}


def get_transcript_from_youtube(url, add_metadata=True, save_to_file=None):
    # filter for manually created transcripts

    video_id = parse_video_id(url)
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(['en-US', 'en'])
    segments = combine_segments(transcript.fetch(), group_size=None)
    transcript = {
        "transcript": {
            "text": ' '.join([s["text"] for s in segments]),
            "segments": segments,
            "language": transcript.language_code,
            "transcription_source": "youtube_auto_generated" if transcript.is_generated else "youtube_manual",
        }
    }
    if add_metadata:
        transcript = add_video_metadata_to_transcript(transcript, url)
    if save_to_file:
        if save_to_file == 'json':
            formatter = JSONFormatter()
        else:
            formatter = TextFormatter()
        formatted = formatter.format_transcript(transcript, indent=4)
        with open(f'{video_id}.{save_to_file}', 'w', encoding='utf-8') as file:
            file.write(formatted)

    return transcript


def combine_segments(segments, group_size: Union[int, None] = 5, character_size=300):
    """
    Combine segments based on either a max group size or a max character size.
    """
    combined_segments = []
    current_group = []
    for segment in segments:
        current_group.append(segment)
        current_group_combined = combine_group(current_group)
        if (group_size is None and len(current_group_combined['text']) >= character_size) \
                or len(current_group) == group_size:
            combined_segments.append(current_group_combined)
            current_group = []
    if current_group:
        combined_segments.append(combine_group(current_group))
    return combined_segments


def combine_group(group):
    text = ' '.join([s["text"] for s in group])
    start = int(group[0]["start"])
    end = int(group[-1]["start"] + group[-1]["duration"])
    duration = end - start
    return {
        "text": text,
        "start": start,
        "duration": duration,
        "end": end
    }


def add_video_metadata_to_transcript(video_transcript, url):
    video = YouTube(url)
    print('video', video)
    video_metadata = {
        "id": video.video_id,
        "thumbnail": video.thumbnail_url,
        "title": video.title,
        "views": video.views,
        "length": video.length,
        "url": f"https://www.youtube.com/watch?v={video.video_id}",
    }
    segments_with_metadata = [{
        **segment,
        **video_metadata,
        'id': f"{video_metadata['id']}-t{segment['start']}",
        "url": f"https://www.youtube.com/watch?v={video.video_id}&t={segment['start']}",
        'video_id': video.video_id,
    } for segment in video_transcript['transcript']['segments']
    ]

    return {
        "video": video_metadata,
        "transcript": {
            **video_transcript['transcript'],
            "segments": segments_with_metadata
        },
    }
