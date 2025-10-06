import base64


"""
{
    document: data,
    metadata: {
        user_id:,
        mail_id:,
        created_at:,
        updated_at:,
        sent_by:
        sent_to:
        title:
        header:
        footer:
        cc: []
}
"""




def decode_mail(data):
    pass

def store_start_history(historyId):
    with open("mail_history.txt", 'w') as file:
        file.write(historyId)

def get_start_history():
    with open("mail_history.txt", 'r') as file:
        historyId = int(file.read())
        return historyId


class VectorStore:
    def __init__(self, client, collection_name):
        self.client = client
        self.collection = client.get_or_create_collection(collection_name, metadata={"hnsw:space":"cosine"})
    
    def add_documents(self, documents, ids):
        pass

    def query_documents(self, query, n_results=1):
        pass

    def create_embeddings(self, text):
        pass