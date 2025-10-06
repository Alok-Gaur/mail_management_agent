from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
import requests
from jose import jwt
from secrets import config


router = APIRouter(tags=['Authentication'])


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