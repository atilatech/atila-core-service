from datetime import timedelta
import json
import urllib
from typing import Union

import requests

from atlas.config import HUGGING_FACE_API_KEY, HUGGING_FACE_ENDPOINT_URL


def convert_seconds_to_string(seconds):
    days, seconds = divmod(seconds, 86400)
    return str(timedelta(days=days, seconds=seconds)).split(',')[-1].strip()


def parse_video_id(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)

    # Check if the URL is a YouTube URL
    if parsed_url and parsed_url.netloc in ['www.youtube.com', 'youtu.be']:
        # Extract the video ID from the path or query parameters
        if parsed_url.netloc == 'www.youtube.com':
            video_id = urllib.parse.parse_qs(parsed_url.query)['v'][0]
        else:
            video_id = parsed_url.path.split('/')[-1]
        return video_id
    else:
        return None


# TODO: send_transcription_request, send_encoding_request, and send_generate_answer_request can be combined togeter
def send_transcription_request(url: str):
    payload = json.dumps({
        "inputs": "",  # inputs key is not used but our endpoint requires it
        # see: https://huggingface.co/docs/inference-endpoints/guides/custom_handler#2-create-endpointhandler-cp
        "video_url": url,
    })
    headers = {
        'Authorization': f'Bearer {HUGGING_FACE_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", HUGGING_FACE_ENDPOINT_URL, headers=headers, data=payload)
    return response.json()


def send_huggingface_request(payload_args: dict):
    payload = json.dumps({
        "inputs": "",  # inputs key is not used but our endpoint requires it
        **payload_args
    })
    headers = {
        'Authorization': f'Bearer {HUGGING_FACE_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", HUGGING_FACE_ENDPOINT_URL, headers=headers, data=payload)
    return response.json()


def send_encoding_request(query: Union[str, list]):
    payload = json.dumps({
        "inputs": "",  # inputs key is not used but our endpoint requires it
        "query": query,
    })
    headers = {
        'Authorization': f'Bearer {HUGGING_FACE_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", HUGGING_FACE_ENDPOINT_URL, headers=headers, data=payload)
    return response.json()


def send_generate_answer_request(query: Union[str, list], context):
    payload = json.dumps({
        "inputs": "",  # inputs key is not used but our endpoint requires it
        "query": query,
        "long_form_answer": True,
        "context": context,
    })
    headers = {
        'Authorization': f'Bearer {HUGGING_FACE_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", HUGGING_FACE_ENDPOINT_URL, headers=headers, data=payload)
    return response.json()
