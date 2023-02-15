from atlas.models import Document
from atlas.models_utils import YOUTUBE_URL_PREFIX
from atlas.serializers import DocumentSerializer
from atlas.transcribe import transcribe_and_search_video
from atlas.utils import parse_video_id, send_huggingface_request


def combine_segments(segments, max_length=1000):
    combined_segments = []
    if len(segments) < 1:
        return combined_segments

    current_segment = {"text": "", "end": 0}
    for index, segment in enumerate(segments):
        segment_keys = segment.keys()
        if len(current_segment["text"]) + len(segment["text"]) <= max_length:
            for key in segment_keys:
                if key not in current_segment:
                    current_segment[key] = segment[key]
            current_segment["text"] += segment["text"]
            current_segment["length"] = len(current_segment["text"])
            if "duration" in segment and "duration" in current_segment:
                current_segment["duration"] += segment["duration"]
            current_segment["end"] = segment["end"]
        else:
            combined_segments.append(current_segment)
            current_segment = segment
    combined_segments.append(current_segment)
    return combined_segments


def get_evenly_spaced_elements(arr, elements_to_keep=10):
    if len(arr) <= elements_to_keep:
        return arr
    else:
        step = len(arr) // elements_to_keep
        evenly_spaced_elements = [arr[i] for i in range(0, len(arr), step) if i < len(arr)]
        while len(evenly_spaced_elements) < elements_to_keep and len(arr) > 0:
            evenly_spaced_elements.append(arr[-1])
        return evenly_spaced_elements


def summarize_video(url):
    video_id = parse_video_id(url)

    document_filter = Document.objects.filter(url=f"{YOUTUBE_URL_PREFIX}?v={video_id}")
    if not document_filter.exists():
        print(f"No video with url {url} exists. Transcribing video first before summarizing")
        transcribe_and_search_video('', url)

    video = document_filter.first()
    if len(video.summaries) == 0:
        segments = get_evenly_spaced_elements(combine_segments(video.segments))
        summaries = send_huggingface_request({"summarize": True, "segments": segments})['summary']
        if "error" in summaries:
            return {"error": summaries}
        video.summaries = summaries
        video.save()

    return {"video": DocumentSerializer(video).data}
