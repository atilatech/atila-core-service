import os

HUGGING_FACE_ENDPOINT_URL = "https://qr7d334cs4mibwrq.us-east-1.aws.endpoints.huggingface.cloud"

HUGGING_FACE_API_KEY = os.environ.get('HUGGING_FACE_API_KEY', None)

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', None)
