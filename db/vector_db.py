import chromadb
from chromadb.config import Settings
# client = chromadb.get_or_create_collection('test')

def get_chroma_client():
    client = chromadb.Client(Settings(
        persist_directory=".chromadb",
    ))
    return client

def get_chroma_collection(collection_id: int):
    client = get_chroma_client()
    collection_name = f"user_{collection_id}_emails"
    collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space":"cosine"})
    return collection