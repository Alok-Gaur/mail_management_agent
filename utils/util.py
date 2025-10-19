import base64
import json
from fastapi import HTTPException, status
from base64 import urlsafe_b64decode
from datetime import datetime

"""
{
    document: data,
    metadata: {
        user_id:,
        mail_id:,
        history_id:,
        created_at:,
        updated_at:,
        sent_by:
        sent_to:
        title:
        header:
        footer:
        cc: []
        bcc:[]
}
"""




def decode_mail(data, encoding='UTF-8'):
    try:
        return base64.b64decode(data).decode(encoding)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

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



class ParseUtil:
    """Parse documents or requests"""

    def gmail_messages(self, message:dict) -> dict:
        """ Extract message details from gmail service """
        extracted_data = {}

        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        parts = payload.get('parts', [])

        print("message is ", message)

        def get_header(name):
            for header in headers:
                if header['name'].lower() == name.lower():
                    return header['value']
            return None

        # Decode message body
        def decode_body():
            if 'data' in payload.get('body', {}):
                return urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            for part in parts:
                if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                    return urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            return ""

        extracted_data= {
            "document": decode_body(),
            "metadata": {
                # "user_id": user_id,
                "mail_id": message.get('id'),
                "history_id": message.get('historyId'),
                "created_at": datetime.utcfromtimestamp(int(message.get('internalDate')) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "stored_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "sent_by": get_header('From'),
                "sent_to": get_header('To'),
                "subject": get_header('Subject'),
                "header": get_header('X-Header') or "",  # Custom header if any
                "cc": get_header('Cc') or "",
                "bcc": get_header('Bcc') or ""
            }
        }

        return extracted_data

# Usage
# service = build('gmail', 'v1', credentials=your_credentials)
# messages = extract_message_details(service)
# print(messages)