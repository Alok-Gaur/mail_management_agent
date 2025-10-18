from fastapi import APIRouter, Depends, HTTPException, status
from auth.dependency import get_current_user
from sqlalchemy.orm import Session
from db.relational_db import get_db
from fastapi.responses import Response
from utils.google import Services
from google.oauth2.credentials import Credentials
import json
import utils.google as google


from fastapi.responses import RedirectResponse
from models.relational_models import User
from dataclasses import asdict

router = APIRouter(tags=['Users'])

@router.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user), 
                  db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    data = {
        "email": user.email,
        "fname": user.fname, 
        "lname": user.lname,
    }
    return Response(status_code=status.HTTP_200_OK, content=json.dumps(data))


@router.delete("/users/me")
def delete_user_me(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_200_OK, content="User deleted successfully")


@router.get("/users/credentials")
def cred(current_user: dict = Depends(get_current_user), 
        db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    google_creds = Services(db, user.id)
    creds = google_creds.get_credentials()
    print(creds)
    if isinstance(creds, Credentials):
        print("It isinstance")
        google.start_watch(creds)
    else:
        return creds

    # print(creds.token)