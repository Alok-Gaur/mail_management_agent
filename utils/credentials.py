from os import path
import json
import utils.util as util
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.relational_models import UserSecret

SCOPES = ['https://mail.google.com/']
TOPIC_NAME = "projects/project-use-a/topics/new_mail"



class GoogleCredentials:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
    
    def get_credentials(self):
        credentials = self.db.query(UserSecret).filter(UserSecret.user_id == self.user_id).first()
        if credentials:
            if credentials.client_token:
                creds = Credentials.from_authorized_user_info(json.loads(credentials.client_token), SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    credentials.client_token = creds.to_json()
                    self.db.commit()
                    return creds
            elif credentials.client_secret:
                flow = InstalledAppFlow.from_client_config(json.loads(credentials.client_secret), SCOPES)
                


        
        else:
            raise Exception("No credentials found for user")
    





# Get Google Api Credentials
def get_google_credentials():
    creds = None
    if path.exists("secrets/token.json"):
        creds = Credentials.from_authorized_user_file("secrets/token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("secrets/credentials.json")
            creds = flow.run_local_server(port=0)
        
        with open("secrets/token.json", 'w') as token:
            token.write(creds.to_json())
    return creds


# start watch for new mail
def start_watch(creds):
    try:
        services =  build("gmail", "v1", credentials=creds)

        request_body = {
            'labelIds':['INBOX'],
            'topicName': TOPIC_NAME,
        }

        response = services.users().watch(userId='me', body=request_body).execute()

    except Exception as e:
        print(e)
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
    historyId = util.get_start_history()
    results = services.users().history().list(
        userId='me',
        startHistoryId=historyId,
        historyTypes=['messageAdded']
    ).execute()

    history_records = results.get('history')
    message_ids = []
    for record in history_records:
        for msg in record.get('messagesAdded', []):
            message_id = msg['message']['id']
            message_ids.append(message_id)
            print(get_message_details(services, message_id))
            print("="*30, "\n\n")
    
    return message_ids

def get_message_details(services, message_id=17733):
    message = services.users().messages().get(userId='me', id=message_id, format='full').execute()
    print("Subject:", next(header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject'))
    return message

if __name__ == "__main__":
    creds = get_google_credentials()
    message_ids = mail_by_id(creds)
    # print(get_message_details(creds))

    # start_watch(creds)
    # print("mail is: ", get_message_details('16185194184222352'))