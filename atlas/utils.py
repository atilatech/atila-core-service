import json
import logging
import urllib.parse
from datetime import timedelta

import requests
from requests import HTTPError

from atlas.config import POPLAR_API_KEY, HUGGING_FACE_API_KEY, HUGGING_FACE_ENDPOINT_URL, OPENAI_API_KEY

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


def send_ai_request(request_args: dict, provider="huggingface"):
    headers = {}
    if provider in ['poplar', 'huggingface']:
        request_args = {
            "inputs": "",  # inputs key is not used but Hugging Face endpoint requires it
            **request_args
        }
    if provider == "poplar":
        url = "https://api.poplarml.com/infer"
        request_body = {
            "apiKey": POPLAR_API_KEY,
            "modelId": "atila-atlas",
            "modelInput": request_args,
        }
        headers["Content-Type"] = "application/json"
    elif provider == "huggingface":
        url = HUGGING_FACE_ENDPOINT_URL
        request_body = request_args
        headers["Authorization"] = f"Bearer {HUGGING_FACE_API_KEY}"
        headers["Content-Type"] = "application/json"
    elif provider == "openai":
        prompt = "Given the following context. Answer the question using the provided context." \
                 "Indicate which youtube video you are referenced in your answer using numbered footnotes." \
                 "and the link of the source." \
                 f"Context:\n\n {request_args['context']}" \
                 f"\n\nQuestion: {request_args['question']}" \
                 f"\n\nAnswer:"
        request_body = {
          "model": "text-davinci-003",
          "prompt": prompt,
          "temperature": 0,
          "max_tokens": 2000,
          "top_p": 1,
          "frequency_penalty": 0,
          "presence_penalty": 0,
          "stop": ["\n"]
        }
        url = "https://api.openai.com/v1/completions"
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"
        headers["Content-Type"] = "application/json"
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

    request_body = json.dumps(request_body)
    response = requests.post(url, data=request_body, headers=headers)
    response.raise_for_status()
    if 'error' in response.json():
        raise HTTPError(response.json())

    return response.json()
