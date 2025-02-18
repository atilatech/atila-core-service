import os

import pytube
import stripe
from pytube import Playlist, Channel
from googleapiclient.discovery import build

pytube.innertube._default_clients['ANDROID'] = pytube.innertube._default_clients['WEB']

price_per_video = 1
price_per_hour = 1

# stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
STRIPE_TRANSCRIBE_PLAYLIST_PRODUCT_ID = os.getenv('STRIPE_TRANSCRIBE_PLAYLIST_PRODUCT_ID')
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

MAX_VIDEOS_TO_RETRIEVE = 100


def get_videos_from_playlist(url, limit=MAX_VIDEOS_TO_RETRIEVE):
    playlist = Playlist(url)

    videos = []

    if limit is None or limit > MAX_VIDEOS_TO_RETRIEVE:
        limit = MAX_VIDEOS_TO_RETRIEVE

    playlist_info = {
        "title": playlist.title,
        "url": playlist.playlist_url
    }

    for video in playlist.videos:
        playlist_info['total_videos_count'] = len(playlist.video_urls)
        videos.append({
            "title": video.title,
            "url": video.watch_url,
            "length": video.length
        })
        if len(videos) == limit:
            break

    return {
        "playlist": playlist_info,
        "videos": videos
    }


def get_videos_from_channel(url: str):
    if '@' in url:
        username = url.split('@')[-1]
        request = youtube.search().list(
            part="snippet",
            q=username,
            type="channel"
        )
        response = request.execute()
        if len(response['items']) > 0:
            channel_id = response['items'][0]['id']['channelId']
        else:
            raise Exception(f'No matching channels found for {url}')
    else:
        channel = Channel(url)
        channel_id = channel.channel_id

    # Retrieve the channel's uploads playlist ID
    channels_response = youtube.channels().list(part="snippet,contentDetails", id=channel_id).execute()

    playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Retrieve the videos from the uploads playlist
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    result = get_videos_from_playlist(playlist_url)

    channel_info = {
        "title": channels_response["items"][0]["snippet"]["title"],
        "url": channel_url,
    }

    return {
        "channel": channel_info,
        **result
    }


def generate_cost_explanation(metadata):
    price_for_video_count = metadata["price_for_video_count"]
    price_for_video_length = metadata["price_for_video_length"]
    total_cost = metadata["total_cost"]
    total_length_hours = metadata["total_length_hours"]
    video_count = metadata["video_count"]
    title = metadata["title"]
    videos_type = metadata["type"]

    explanation = f"Cost breakdown for transcribing {title} {videos_type}:\n"
    explanation += f"  - Price for {video_count} videos: ${price_for_video_count}\n"
    explanation += f"  - Price for {total_length_hours} hours of video: ${price_for_video_length}\n"
    explanation += f"Total cost: ${total_cost}"

    return explanation


def calculate_cost_for_transcribing_a_collection(url, metadata=None):
    if metadata is None:
        metadata = {}

    if '/playlist' in url:
        metadata['type'] = 'playlist'
        result = get_videos_from_playlist(url)
        metadata['title'] = result['playlist']['title']
        metadata['url'] = result['playlist']['url']
    else:
        metadata['type'] = 'channel'
        result = get_videos_from_channel(url)
        metadata['title'] = result['channel']['title']
        metadata['url'] = result['channel']['url']

    metadata['total_videos_count'] = result['playlist']['total_videos_count']

    videos = result['videos']
    price_for_video_count = len(videos) * price_per_video
    metadata['price_per_video'] = price_per_video
    metadata['price_for_video_count'] = price_for_video_count

    video_count = len(videos)
    metadata['video_count'] = video_count

    total_length_hours = sum([video["length"] for video in videos]) / (60 * 60)
    total_length_hours = '{0:.2f}'.format(total_length_hours)
    # pycharm type hinting thought the price_for_video_length was a string so casting to float to prevent ambiguity
    price_for_video_length = float(total_length_hours * price_per_hour)

    metadata['price_per_hour'] = price_per_hour
    metadata['total_length_hours'] = total_length_hours
    metadata['price_for_video_length'] = price_for_video_length

    metadata['total_cost'] = '{0:.2f}'.format(price_for_video_count + price_for_video_length)

    currency = "usd"
    stripe_price = stripe.Price.create(
        unit_amount=int((price_for_video_count + price_for_video_length) * 100),
        currency=currency,
        product=STRIPE_TRANSCRIBE_PLAYLIST_PRODUCT_ID,
    )

    payment_link = stripe.PaymentLink.create(
        line_items=[
            {
                "price": stripe_price.id,
                "quantity": 1,
            },
        ],
        metadata=metadata
    )

    metadata['payment_link'] = payment_link['url']
    metadata['cost_breakdown_text'] = generate_cost_explanation(metadata)

    return metadata
