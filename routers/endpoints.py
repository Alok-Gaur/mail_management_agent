from fastapi import APIRouter, status, Request
import utils.credentials as credentials
import json
router = APIRouter(tags=['Web Hooks'])

# WebHook to get the latest mail id
# https://mail-management.ngrok.io/mail-hook
# ngrok http 8000 --domain=mail-management.ngrok.io
# ngrok http --url=openly-fluent-dogfish.ngrok-free.app 8000
@router.post("/mail-hook")
async def get_mail(request:Request):
    body = await request.json()
    message_data = body.get("message", {}).get("data")
    if message_data:
        import base64
        
        creds = credentials.get_google_credentials()
        decoded = json.loads(base64.b64decode(message_data).decode("utf-8"))
        print("New mail notification:", decoded)
        
        print("\n\nFetching message ids....")
        message_id = credentials.mail_by_id(creds, decoded.get("historyId"))
    return {"status": "received"}
