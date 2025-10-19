from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from env_secrets import config
from models.relational_schema import SignUpSchema
from models.relational_models import User, RefreshToken, UserSecret
from auth.handlers import AuthHandler, GoogleAuthHandler
from sqlalchemy.orm import Session
from db.relational_db import get_db
from datetime import datetime, timedelta
from auth.dependency import get_current_user
from urllib.parse import urlencode

import json
from seed import seed_database


router = APIRouter(tags=['Authentication'])

# Google Authentication and Callbacks

# Redirect to Google's OAuth 2.0 server
@router.get("/auth/google")
async def login_google():
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://mail.google.com/ https://www.googleapis.com/auth/userinfo.email",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return RedirectResponse(url=url)

# Handle the OAuth 2.0 server response
@router.get("/auth/callback")
async def auth_google(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth2 callback and exchange code for tokens"""

    # Authenticate with Google and get user consent for access token and refresh token
    google_auth = GoogleAuthHandler()
    token_response = google_auth.get_token(code=code)
    print(token_response)
    google_access_token = token_response.get("access_token")
    google_refresh_token = token_response.get("refresh_token")
    google_expire_time = token_response.get("expires_in")
    user_info = google_auth.user_info(google_access_token)

    user = db.query(User).filter(User.email == user_info.get("email")).first()
    print("The user table we get while query is ", user_info.get("email"))

    auth_handler = AuthHandler()
    access_token = auth_handler.create_access_token(data={"sub": user_info.get("email")}, expires_delta=None)
    refresh_token = auth_handler.create_refresh_token()
    if not user:    # Only for new users signup
        try:
            if user_info:
                user_info = user_info.json()
                
                user_info = User(
                    username = user_info.get("email").split("@")[0],
                    email = user_info.get("email"),
                    fname = user_info.get("given_name"),
                    lname = user_info.get("family_name", None),
                    google_login = True
                )
                db.add(user_info)
                db.flush()
                
                new_token = RefreshToken(token=refresh_token, user_id=user_info.id)
                
                user_secret = UserSecret(
                    client_token = google_access_token,
                    refresh_token = google_refresh_token,
                    expires_at = datetime.utcnow() + timedelta(seconds=google_expire_time) if google_expire_time else None,
                    user_id=user_info.id
                )

                db.add(new_token)
                db.add(user_secret)
                db.commit()
                seed_database(db, user_info.id) # Seed default settings for new user
        except Exception as e:
            db.rollback()
            print("Error during Google OAuth:", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    # Old user login and token update
    else:
        print("old user", refresh_token)
        new_refresh_token = RefreshToken(token=refresh_token, user_id=user.id)
        db.add(new_refresh_token)

        user_secret = db.query(UserSecret).filter(UserSecret.user_id == user.id).first()
        if user_secret:
            user_secret.client_token = google_access_token
            user_secret.refresh_token = google_refresh_token
            user_secret.expires_at = datetime.utcnow() + timedelta(seconds=google_expire_time) if google_expire_time else None
        else:
            user_secret = UserSecret(
                client_token = google_access_token,
                refresh_token = google_refresh_token,
                expires_at = datetime.utcnow() + timedelta(seconds=google_expire_time) if google_expire_time else None,
                user_id=user.id 
            )
        db.add(user_secret)
        db.commit()
        db.refresh(user_secret)
        print("database written", user_secret.updated_at)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}) # [user_info.json(), access_token]


@router.get("/auth/refresh-token")
async def refresh_token(token: str, db: Session = Depends(get_db)):
    refresh_token  = db.query(RefreshToken.token, RefreshToken.user_id)\
                                    .filter(RefreshToken.token == token)\
                                    .filter(RefreshToken.revoked == False)\
                                    .filter(RefreshToken.expires_at > datetime.now(datetime.timezone.utc)).first()
    
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    auth_handler = AuthHandler()
    access_token = auth_handler.create_access_token(data={"sub": user.email}, expires_delta=None)
    refresh_token = auth_handler.create_refresh_token()

    new_refresh_token = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(new_refresh_token)
    db.commit()
    # return jwt.decode(token, config.GOOGLE_CLIENT_SECRET, algorithms=["RS256"])

    return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})


# Manual authentication from user name and password
@router.post("/auth/signup")
async def signup(user: SignUpSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing:
        if existing.email == user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    auth_handler = AuthHandler()
    try:
        user.password = auth_handler.hash_password(user.password)
        access_token = auth_handler.create_access_token(data={"sub": user.email}, expires_delta=None)
        refresh_token = auth_handler.create_refresh_token()
        
        new_user = User(**user.dict())
        db.add(new_user)
        db.flush()
        new_token = RefreshToken(token=refresh_token, user_id=new_user.id)
        db.add(new_token)
        db.commit()   
        seed_database(db, new_user.id) # Seed default settings for new user
    except Exception as e:
        db.rollback()
        print("Error adding user:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    # print("User added:", new_user)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})

@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    auth_handler = AuthHandler()
    if not user or not auth_handler.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = auth_handler.create_access_token(data={"sub": user.email}, expires_delta=None)
    refresh_token = auth_handler.create_refresh_token()

    print("Till Here")
    new_refresh_token = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    print("Access Token: ", access_token)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})
    