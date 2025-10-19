from os import path
import json
import utils.util as util
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from models.relational_models import UserSecret, WatchHistory
from env_secrets import config
from fastapi import HTTPException, status

from urllib.parse import urlencode
from base64 import b64decode
from typing import List
from sqlalchemy.exc import SQLAlchemyError

SCOPES = ['https://mail.google.com/']
TOPIC_NAME = "projects/project-use-a/topics/new_mail"
TOKEN_URL = "https://oauth2.googleapis.com/token"



class Services:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.services = None
        
        # Elegibility check of the  user,
        # eligible if have token and refresh token
        secret = db.query(UserSecret).filter(UserSecret.user_id == user_id).first()
        if secret.client_token and secret.refresh_token:
            self.valid = True
        else: 
            self.valid = False
    

    def subscribe_service(self) -> str:
        credentials = self.db.query(UserSecret).filter(UserSecret.user_id == self.user_id).first()
        email = ""
        if credentials:
            email = credentials.user.email
        
        params = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "https://mail.google.com/ https://www.googleapis.com/auth/userinfo.email",
            "access_type": "offline",
            "prompt": "consent", 
            "login_hint": email
        }

        url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
        return {"Authentication URL": url}

    def get_credentials(self)-> Credentials:
        credentials = self.db.query(UserSecret).filter(UserSecret.user_id == self.user_id).first()
        try:
            # Check if credentials exist and valid
            if credentials and self.valid:
                creds = Credentials(
                    token=credentials.client_token,
                    refresh_token=credentials.refresh_token,
                    token_uri=TOKEN_URL,
                    client_id=config.GOOGLE_CLIENT_ID,
                    expiry= credentials.expires_at,
                    client_secret=config.GOOGLE_CLIENT_SECRET,
                    scopes=SCOPES
                )

                # Stores token if refreshed
                if credentials.client_token != creds.token:
                    credentials.client_token = creds.token
                    self.db.commit()
            
            return creds
        except Exception as e:
            print(4, str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            
    
    def build_service(self, service_name, version):
        if self.valid:
            try:
                self.services = build(service_name, version, credentials=self.get_credentials())
                return self.services
            except Exception as e:
                print(3 , str(e))
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google authentication required")
    
    def start_watch(self, labels:list[str] = ["INBOX"]) -> dict:
        services = self.services or self.build_service("gmail", "v1")

        request_body = {
            'labelIds':labels,
            'topicName': TOPIC_NAME,
        }

        response = services.users().watch(userId='me', body=request_body).execute()

        return {"service_start":"watch", **response}

    def stop_watch(self) -> dict:
        services = self.services or self.build_service("gmail", "v1")
        response = services.users().stop(userId='me').execute()
        return response
    
    def get_mail_ids(self, history_id: int) -> list:
        """ Fetch mail ids from history id
        Args:
            history_id int: History Id sent by the pubsub to get the email ids
        Returns:
            list: List of mail ids
        """
        services = self.services or self.build_service("gmail", "v1")
        try:
            results = services.users().history().list(
                userId='me',
                startHistoryId=history_id,
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
                    break
            return message_ids
        except Exception as e:
            print(5, str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

    def store_mail(self, mail_ids:List[int]) -> None:
        """
        Fetch and store mail using mail ids

        args:
            mail_ids (List[int]): List of mail ids

        """
        services = self.services or self.build_service("gmail", "v1")
        for mail_id in mail_ids:
            try:
                message = services.users().messages().get(userId='me', id=mail_id, format='full').execute()
                parsed_data = util.ParseUtil().gmail_messages(message)
                parsed_data['metadata']["user_id"] = self.user_id
                print("Storing mail data:", parsed_data)
                break
            except Exception as e:
                print(6, str(e))
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    def decode(self, data, encoding='UTF-8') -> str:
        """ Decode base64 encoded data"""
        try:
            return json.loads(b64decode(data).decode(encoding))
        except Exception as e:
            print(2, str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    def manage_hook(self, history_id: int):
        """ Manage incoming webhook from google pubsub service"""
        services = self.services or self.build_service("gmail", "v1")

        try:
            # maintain history id in the database
            check_history = self.db.query(WatchHistory.id).filter(WatchHistory.history_id==history_id)\
                                .filter(WatchHistory.user_id == self.user_id).first()
        except SQLAlchemyError:
            self.db.rollback()
            check_history = None

        if not check_history:
            update_watch_history = WatchHistory(
                history_id = history_id, 
                added_by = "hook",
                user_id = self.user_id
            )
            self.db.add(update_watch_history)
            self.db.commit()


        try:
            message_ids = self.get_mail_ids(history_id)
            message = self.store_mail(message_ids)
            return message
        except Exception as e:
            print('1', str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        


            # print(response)
            # print("No credentials found for user")
            # return []
            
                # creds = Credentials.from_authorized_user_info(json.loads(credentials.client_token), SCOPES)
                # if creds and creds.expired and creds.refresh_token:
                #     creds.refresh(Request())
                #     credentials.client_token = creds.to_json()
                #     self.db.commit()
                #     return creds
        #     elif credentials.client_secret:
        #         flow = InstalledAppFlow.from_client_config(json.loads(credentials.client_secret), SCOPES)
        
        # else:
        #     raise Exception("No credentials found for user")
    
    





# Get Google Api Credentials from json file
# def get_google_credentials():
#     creds = None
#     if path.exists("env_secrets/token.json"):
#         creds = Credentials.from_authorized_user_file("env_secrets/token.json", SCOPES)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("env_secrets/credentials.json", SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         with open("env_secrets/token.json", 'w') as token:
#             token.write(creds.to_json())
#     return creds


# start watch for new mail
def start_watch(creds):
    try:
        services =  build("gmail", "v1", credentials=creds)

        request_body = {
            'labelIds':['INBOX'],
            'topicName': TOPIC_NAME,
        }

        response = services.users().watch(userId='me', body=request_body).execute()

        print("watch started: ", response)
    except Exception as e:
        print(e)






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

# if __name__ == "__main__":
#     creds = get_google_credentials()
#     message_ids = mail_by_id(creds)
    # print(get_message_details(creds))

    # start_watch(creds)
    # print("mail is: ", get_message_details('16185194184222352'))