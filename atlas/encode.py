import pinecone
from tqdm import tqdm

from atlas.config import PINECONE_API_KEY
from atlas.utils import parse_video_id, send_ai_request

sentence_transformer_model_model_id = "multi-qa-mpnet-base-dot-v1"
PINECONE_INDEX_ID = "youtube-search"
batch_size = 64

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment="us-west1-gcp"
)

pinecone_index = pinecone.Index(PINECONE_INDEX_ID)


def initialize_pinecone_index():
    dimensions = 768
    if PINECONE_INDEX_ID not in pinecone.list_indexes():
        pinecone.create_index(
            PINECONE_INDEX_ID,
            dimensions,
            metric="dotproduct"
        )


def does_video_exist_in_pinecone(video_url):
    # create a placeholder vector of zeros to see if any vectors with the
    # given video_id match.
    video_id = parse_video_id(video_url)
    dimension = pinecone_index.describe_index_stats()['dimension']
    query_response = pinecone_index.query(
        top_k=1,
        vector=[0] * dimension,
        filter={
            "video_id": {"$eq": video_id}
        }
    )
    return len(query_response['matches']) > 0


def upload_transcripts_to_vector_db(transcripts):
    # loop through in batches of 64
    for i in tqdm(range(0, len(transcripts), batch_size)):
        # find end position of batch (for when we hit end of data)
        i_end = min(len(transcripts), i + batch_size)
        # extract the metadata like text, start/end positions, etc
        batch_meta = [{
            **row
        } for row in transcripts[i:i_end]]
        # create the embedding vectors
        batch_vectors = [
            row.pop('vectors') for row in batch_meta
        ]
        # extract IDs to be attached to each embedding and metadata
        batch_ids = [
            row['id'] for row in batch_meta
        ]
        # 'upsert' (insert) IDs, embeddings, and metadata to index
        to_upsert = list(zip(
            batch_ids, batch_vectors, batch_meta
        ))
        pinecone_index.upsert(to_upsert)
        print(f'Uploaded Batches: {i} to {i_end}')


def query_model(query, video_id=""):
    """
    Return a list of matches for a given query and then optionally generate a summarized answer based on the matches.
    """
    encoded_query = send_ai_request({"query": query})
    metadata_filter = {"video_id": {"$eq": video_id}} if video_id else None
    vectors = encoded_query['encoded_segments'][0]['vectors']

    results = pinecone_index.query(vectors, top_k=5,
                                   include_metadata=True,
                                   filter=metadata_filter).to_dict()

    return results
