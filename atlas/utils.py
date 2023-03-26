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
        request_args = json.dumps({
            "inputs": "",  # inputs key is not used but Hugging Face endpoint requires it
            **request_args
        })
    if provider == "poplar":
        url = "https://api.poplarml.com/infer"
        request_body = {
            "apiKey": POPLAR_API_KEY,
            "modelId": "atila-atlas",
            "modelInput": request_args,
        }
    elif provider == "huggingface":
        url = HUGGING_FACE_ENDPOINT_URL
        request_body = request_args
        headers["Authorization"] = f"Bearer {HUGGING_FACE_API_KEY}"
        headers["Content-Type"] = "application/json"
    elif provider == "openai":

        # example_prompt may not be necessary
        example_prompt = """
        1: steve madden makes a good shoe and i would also recommend topshop i think these are like kind of a british style shoe so i think they have some on their website as well. this took me so long to figure out but victoria's secret broads suck somehow they have managed to throw shoes I would wear with this outfit probably airforces if we're being honest but I feel like it would also look really cute with some platform sandals alright

        2: so here's the next outfit I'm wearing this skirt again from Tilly's and then I just have this like halter kind of top not really halter I don't dress with chunky platform shoes or boots with some type of hardware on them i just think it looks really cool and casual and it's such a foolproof combination.
        
        1: https://www.youtube.com/watch?v=qaIBka_zHKI
        
        2: https://www.youtube.com/watch?v=PCOo8AW4oI0
        
        question: what shoes should I wear
        
        answer: You should wear Airforces [1] or chunky platform shoes or boots with some type of hardware on them [2]
        1: https://www.youtube.com/watch?v=qaIBka_zHKI
        2: https://www.youtube.com/watch?v=PCOo8AW4oI0
        """
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
        request_body = json.dumps(request_body)
        url = "https://api.openai.com/v1/completions"
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"
        headers["Content-Type"] = "application/json"
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

    print('request_body', request_body)
    response = requests.post(url, data=request_body, headers=headers)
    if 'error' in response.json():
        raise HTTPError(response.json())
    response.raise_for_status()

    return response.json()
