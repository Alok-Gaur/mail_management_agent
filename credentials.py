from os import path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://mail.google.com/']
TOPIC_NAME = "projects/project-use-a/topics/new_mail"

def get_google_credentials():
    creds = None
    if path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json")
            creds = flow.run_local_server(port=0)
        
        with open("token.json", 'w') as token:
            token.write(creds.to_json())
    return creds


def start_watch(creds):
    services =  build("gmail", "v1", credentials=creds)

    request_body = {
        'labelIds':['INBOX'],
        'topicName': TOPIC_NAME,
    }

    response = services.users().watch(userId='me', body=request_body).execute()
    print("watch started: ", response)






# SCOPE = ['https://www.googleapis.com/auth/gmail.readonly']

def get_spam(creds):
    request_body = {
        'labelIds':['INBOX'],
        'topicName': TOPIC_NAME,
    }

    service = build('gmail', 'v1', credentials=creds)
    response = service.users().watch(userId='me', body=request_body).execute()
    
    print("Watch Started: ", response)
    # print(results.get("messages", []))



def mail_by_id(creds, id=17624):
    services = build("gmail", "v1", credentials=creds)
    
    results = services.users().history().list(
        userId='me',
        startHistoryId=id,
        # historyTypes=['messageAdded']
    ).execute()

    history_records = results.get('history', [])
    message_ids = []
    print(history_records)
    for record in history_records:
        for msg in record.get('messageAdded', []):
            message_ids.append(msg['message']['id'])
    
    print("New Message Ids: ", message_ids)
    return message_ids

def get_message_details(creds, message_id):
    service = build("gmail", "v1", credentials=creds)
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    print("Subject:", next(header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject'))
    return message

if __name__ == "__main__":
    message_ids = mail_by_id()

    # start_watch()
    # print("mail is: ", get_message_details('16185194184222352'))