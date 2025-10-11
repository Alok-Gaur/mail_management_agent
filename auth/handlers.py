from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from env_secrets import config
import secrets
import requests
import json


class AuthHandler:
    def __init__(self):
        self.secret_key = config.SECRET_KEY
        self.algorithm = config.ALGORITHM
        self.access_token_expire_time = config.ACCESS_TOKEN_EXPIRE_TIME   #In Minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        '''Returns the hashed version of the password'''
        return self.pwd_context.hash(password)

    def verify_password(self, user_password: str, hashed_password: str) -> bool:
        '''Verifies the user password against the hashed password'''
        return self.pwd_context.verify(user_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta) -> str:
        '''Creates a JWT token'''
        to_encode = data.copy()
        if not expires_delta:
            expires_delta = timedelta(minutes=self.access_token_expire_time)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self):
        return secrets.token_urlsafe(32)
    


class GoogleAuthHandler:
    def __init__(self):
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = config.GOOGLE_REDIRECT_URI
    
    def get_token(self, code: str):
        """Exchange authorization code for access token and refresh token"""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        return response.json()
    
    def get_new_token(self, refresh_token: str):
        """Get new access token using refresh token"""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.post(token_url, data=data)
        return response.json() if response.status_code == 200 else None
    
    def user_info(self, access_token: str) -> dict:
        """Get user info using access token"""
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        return user_info.json() if user_info else {}