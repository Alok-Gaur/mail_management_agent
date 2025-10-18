from fastapi import APIRouter, status, Request, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from utils.google import Services
from utils import util
from db.relational_db import get_db
from sqlalchemy.orm import Session
from models.relational_models import User, UserSecret
import json
router = APIRouter(tags=['Web Hooks'])

# WebHook to get the latest mail id
# https://mail-management.ngrok.io/mail-hook
# ngrok http 8000 --domain=mail-management.ngrok.io
# ngrok http --url=openly-fluent-dogfish.ngrok-free.app 8000
@router.post("/mail-hook")
async def get_mail(request:Request, db:Session = Depends(get_db)):
    body = await request.json()
    message_data = body.get("message", {}).get("data")
    
    if message_data:
        mail_details = json.loads(util.decode_mail(message_data))
        email = mail_details.get("emailAddress")
        history_id = mail_details.get("historyId")

        user = await run_in_threadpool(lambda:db.query(User).filter(User.email == email).first())
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        services = Services(db, user.id)
        print("what we get is:", services.valid)
        message = services.manage_hook(history_id)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # creds = google.get_google_credentials()
        # print("\n\nFetching message ids....")
        # message_id = google.mail_by_id(creds, decoded.get("historyId"))
    return {"status": "received"}
