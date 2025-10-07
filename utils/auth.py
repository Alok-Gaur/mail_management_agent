from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from env_secrets import config
import secrets


class AuthHandler:
    secret_key = config.SECRET_KEY
    algorithm = config.ALGORITHM
    access_token_expire_time = config.ACCESS_TOKEN_EXPIRE_TIME   #In Minutes
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        '''Returns the hashed version of the password'''
        return self.__class__.pwd_context.hash(password)
    
    def verify_password(self, user_password: str, hashed_password: str) -> bool:
        '''Verifies the user password against the hashed password'''
        return self.__class__.pwd_context.verify(user_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta) -> str:
        '''Creates a JWT token'''
        to_encode = data.copy()
        if not expires_delta:
            expires_delta = timedelta(minutes=self.__class__.access_token_expire_time)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__class__.secret_key, algorithm=self.__class__.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self):
        return secrets.token_urlsafe(32)
    