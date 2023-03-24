import json
import urllib
from datetime import timedelta

import requests

from atlas.config import POPLAR_API_KEY


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


def send_ai_request(payload_args: dict):
    payload = json.dumps({
        # TODO: Is this still required if we are using PoplarML?
        "inputs": "",  # inputs key is not used but our endpoint requires it
        **payload_args
    })
    print("payload", payload)
    request_body = {"apiKey": POPLAR_API_KEY, "modelId": "atila-atlas", "modelInput": payload}

    response = requests.post("https://api.poplarml.com/infer", json=request_body)
    return response.json()
