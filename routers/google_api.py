from fastapi import APIRouter, HTTPException, Depends, status
from db.relational_db import get_db
from auth.dependency import get_current_user
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, Response
from env_secrets import config
from utils.google import Services


router = APIRouter(tags=["Google API's"])


@router.get("/service/start-watch")
def start_watch(db:Session = Depends(get_db), current_user:Session = Depends(get_current_user)):
    service = Services(db, current_user.id)
    service.start_watch()
    return "Watch Started"

@router.get("/service/stop-watch")
def stop_watch(id: int, db:Session = Depends(get_db)):
    # service = Services(db, id)
    # response = service.stop_watch()
    # print("The Response is", response)
    # return response
    db.rollback()
    return "done"