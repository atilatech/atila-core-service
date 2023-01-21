import sys

import pinecone

from atlas.config import PINECONE_API_KEY
from atlas.encode import PINECONE_INDEX_ID


def delete_by_video_id(video_id):
    video_filter = {
        "video_id": video_id
    }
    delete_using_filter(video_filter)


def delete_using_filter(delete_filter, index_name=PINECONE_INDEX_ID):
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment="us-west1-gcp"
    )

    pinecone_index = pinecone.Index(index_name)
    pinecone_index.delete(
        filter=delete_filter
    )


