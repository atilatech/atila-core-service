import json
import logging
import urllib.parse
from datetime import timedelta

import requests
from requests import HTTPError

from atlas.config import POPLAR_API_KEY, HUGGING_FACE_API_KEY, HUGGING_FACE_ENDPOINT_URL

logger = logging.getLogger(__name__)


def convert_seconds_to_string(seconds):
    return str(timedelta(seconds=seconds)).split(", ")[-1]


def parse_video_id(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.netloc in ["www.youtube.com", "youtu.be"]:
        if parsed_url.netloc == "www.youtube.com":
            video_id = urllib.parse.parse_qs(parsed_url.query)["v"][0]
        else:
            video_id = parsed_url.path.split("/")[-1]
        return video_id
    else:
        return None


def send_ai_request(payload_args: dict, provider="huggingface"):
    headers = {}
    payload_args = json.dumps({
        "inputs": "",  # inputs key is not used but Hugging Face endpoint requires it
        **payload_args
    })
    if provider == "poplar":
        url = "https://api.poplarml.com/infer"
        request_body = {
            "apiKey": POPLAR_API_KEY,
            "modelId": "atila-atlas",
            "modelInput": payload_args,
        }
    elif provider == "huggingface":
        url = HUGGING_FACE_ENDPOINT_URL
        request_body = payload_args
        headers["Authorization"] = f"Bearer {HUGGING_FACE_API_KEY}"
        headers["Content-Type"] = "application/json"
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

    response = requests.post(url, data=request_body, headers=headers)
    if 'error' in response.json():
        raise HTTPError(response.json())
    response.raise_for_status()

    return response.json()
