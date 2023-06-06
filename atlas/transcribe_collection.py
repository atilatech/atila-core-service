import os

import pytube
import stripe
from pytube import Playlist, Channel, YouTube
from googleapiclient.discovery import build

pytube.innertube._default_clients['ANDROID'] = pytube.innertube._default_clients['WEB']

price_per_video = 1
price_per_hour = 0.10

stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
STRIPE_TRANSCRIBE_PLAYLIST_PRODUCT_ID = os.getenv('STRIPE_TRANSCRIBE_PLAYLIST_PRODUCT_ID')
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

MAX_VIDEOS_TO_RETRIEVE = 100


def get_videos_from_playlist(url):
    playlist = Playlist(url)

    videos = []

    playlist_info = {
        "title": playlist.title,
    }

    for video in playlist.videos:
        playlist_info['total_videos'] = len(playlist.video_urls)
        videos.append({
            "title": video.title,
            "url": video.watch_url,
            "length": video.length
        })
        if len(videos) == MAX_VIDEOS_TO_RETRIEVE:
            break

    return {
        "playlist": playlist_info,
        "videos": videos
    }


def get_videos_from_channel(url):
    channel = Channel(url)
    # Retrieve the channel's uploads playlist ID
    channels_response = youtube.channels().list(part="snippet,contentDetails", id=channel.channel_id).execute()
    playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Retrieve the videos from the uploads playlist
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    result = get_videos_from_playlist(playlist_url)

    channel_info = {
        "title": channels_response["items"][0]["snippet"]["title"],
    }

    return {
        "channel": channel_info,
        **result
    }


def calculate_cost_for_transcribing_a_collection(url, metadata=None):
    if metadata is None:
        metadata = {}

    metadata['url'] = url
    if '/playlist' in url:
        result = get_videos_from_playlist(url)
        metadata['title'] = result['playlist']['title']
        metadata['type'] = 'playlist'
    else:
        result = get_videos_from_channel(url)
        metadata['title'] = result['channel']['title']
        metadata['type'] = 'channel'

    videos = result['videos']
    price_for_video_count = len(videos) * price_per_video
    metadata['price_for_video_count'] = price_for_video_count

    video_count = len(videos)
    metadata['video_count'] = video_count

    total_length_hours = sum([video["length"] for video in videos]) / 60
    price_for_video_length = total_length_hours * price_per_hour

    metadata['total_length_hours'] = total_length_hours
    metadata['price_for_video_length'] = price_for_video_length

    metadata['total_cost'] = '{0:.2f}'.format(price_for_video_count+price_for_video_length)

    currency = "usd"
    stripe_price = stripe.Price.create(
        unit_amount=int((price_for_video_count+price_for_video_length) * 100),
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

    return payment_link
