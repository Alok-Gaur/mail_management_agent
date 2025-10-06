from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class MailMetadata(BaseModel):
    mail_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    sent_by: str
    sent_to: str
    title: str
    header: Optional[str] = None
    footer: Optional[str] = None
    labels: List[str] = []
    cc: List[str] = []
    bcc: List[str] = []

class MailDocument(BaseModel):
    document: str
    metadata: MailMetadata