from fastapi import APIRouter, Depends, HTTPException, status
from auth.dependency import get_current_user
from sqlalchemy.orm import Session
from db.relational_db import get_db
from fastapi.responses import Response, JSONResponse
from seed import seed_database
from utils.google import Services
from google.oauth2.credentials import Credentials
import json
from models.relational_schema import *
import utils.google as google


from fastapi.responses import RedirectResponse
from models.relational_models import User, Setting, UserLabels
from dataclasses import asdict

router = APIRouter(tags=['Users'])

""" -----------------------User Related Endpoints----------------------- """

@router.get("/users/me", response_model=ViewUserSchema)
def get_user_details(current_user: dict = Depends(get_current_user), 
                  db: Session = Depends(get_db)):
    """ Get current logged in user details """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


@router.put("/users/me", response_model=ViewUserSchema)
def update_user_details(response: UpdateUserSchema, 
                        current_user: Session = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """ Update current logged in user details """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.fname = response.fname if response.fname else user.fname
    user.lname = response.lname if response.lname else user.lname
    user.username = response.username if response.username else user.username
    db.commit()
    return user


@router.delete("/users/me")
def delete_user_me(user_id: int, db: Session = Depends(get_db)):
    """ Delete the specified user, Not secured endpoint, for testing purposes only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_200_OK, content="User deleted successfully")



""" -----------------------User Settings Endpoints----------------------- """

@router.put("/users/me/settings", response_model=UserSettingsSchema)
def update_user_settings(settings: UserSettingsSchema, 
                         current_user: Session = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    """ Update user settings for current logged in user or create if not exists """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_setting = db.query(Setting).filter(Setting.user_id == user.id).first()
    if user_setting:
        data = settings.model_dump()
        for key, value in data.items():
            setattr(user_setting, key, value)  # Set attribute if it exists
    else:
        user_setting = Setting(**settings.model_dump(), user_id = user.id)
        db.add(user_setting)

    db.commit()
    db.refresh(user_setting)
    return user_setting



""" -----------------------User Labels Endpoints----------------------- """

@router.get("/users/me/labels", response_model=list[UserLabelSchema])
def get_user_labels(current_user: Session = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """ Get the user defined Gmail labels and their description """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    labels = db.query(UserLabels).filter(UserLabels.user_id == user.id).all()
    if not labels:
        return []
    return labels


@router.post("/users/me/labels", response_model=List[UserLabelSchema])
def add_user_labels(labels: List[UserLabelSchema],
                    current_user: Session = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """ Add user defined Gmail labels and their description """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_labels = []
    for label in labels:
        db_label = UserLabels(**label.model_dump(), user_id=user.id)
        new_labels.append(db_label)
    db.add_all(new_labels)
    db.commit()
    db.refresh(new_labels)
    return new_labels


@router.put("/users/me/labels/{label_id}", response_model=UserLabelSchema)
def update_user_labels(label_id: int, label: UserLabelSchema,
                       current_user: Session = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """ Update user defined Gmail labels and their description """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_labels = db.query(UserLabels).filter(UserLabels.user_id == user.id).filter(UserLabels.id == label_id).first()
    if db_labels:
        db_labels.label_name = label.label_name
        db_labels.label_description = label.label_description
        db.commit()
        db.refresh(db_labels)
        return db_labels
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")



""" +++++++++++++++++++++++++++++ Testing API's +++++++++++++++++++++++++++++ """

@router.get("/users/credentials")
def cred(current_user: Session = Depends(get_current_user), 
        db: Session = Depends(get_db)):
    """ Get the Google Credentials of the user 
        Only for testing purposes
    """
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

@router.get("/users/seed")
def seed_user_data(current_user:int,
                   db: Session = Depends(get_db)):
    """ Seed user data for testing purposes """
    user = db.query(User).filter(User.id == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    seed_database(db, user.id)
    return {"detail": "User data seeded successfully."}