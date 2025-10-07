from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
import requests
from jose import jwt
from env_secrets import config
from models.relational_schema import SignUp
from models.relational_models import User, RefreshToken
from utils.auth import AuthHandler
from sqlalchemy.orm import Session
from db.relational_db import get_db


router = APIRouter(tags=['Authentication'])

# Google Authentication and Callbacks

# Redirect to Google's OAuth 2.0 server
@router.get("/auth/google")
async def login_google():
    url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={config.GOOGLE_CLIENT_ID}&redirect_uri={config.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline&prompt=consent"
    return RedirectResponse(url=url)

# Handle the OAuth 2.0 server response
@router.get("/auth/callback")
async def auth_google(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    return [user_info.json(), access_token]


@router.get("/token")
async def token(token: str):
    return jwt.decode(token, config.GOOGLE_CLIENT_SECRET, algorithms=["RS256"])


# Manual authentication from user name and password
@router.post("/auth/signup")
async def signup(user: SignUp, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing:
        if existing.email == user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    auth_handler = AuthHandler()
    try:
        user.password = auth_handler.hash_password(user.password)
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        print("Error adding user:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    print("User added:", new_user)

    return Response(status_code=status.HTTP_201_CREATED)

@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    auth_handler = AuthHandler()
    if not user or not auth_handler.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details="Invalid username or password")
    
    access_token = auth_handler.create_access_token(data={"sub": user.email}, expires_delta=None)
    refresh_token = auth_handler.create_refresh_token()

    new_refresh_token = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    return Response(status_code=status.HTTP_200_OK, content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})
    