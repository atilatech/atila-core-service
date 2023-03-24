import requests
import json

url = 'https://pastebin.com/raw/bTr2kMvw' # url of paste
r = requests.get(url) # response will be stored from url
outfit_ideas_video_segment = r.text  # raw text from url
# print(outfit_ideas_video_segment) # prints content
outfit_ideas_video_segment = json.loads(outfit_ideas_video_segment)
print(outfit_ideas_video_segment[0])

# By ChatGPT: https://imgur.com/a/ek9GI9S
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

combined_segments = get_evenly_spaced_elements(combine_segments(outfit_ideas_video_segment))


payload = {"summarize": True, "segments": combined_segments, "inputs": ""}


request_body = {"apiKey": "[YOUR_API_KEY]", "modelId": "atila-atlas", "modelInput": payload}

response = requests.post("https://api.poplarml.com/infer", json=request_body)

print("response", response.text)