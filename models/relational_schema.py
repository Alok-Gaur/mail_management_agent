from pydantic import BaseModel, EmailStr
from typing import List, Optional


''' User Details Schemas'''
class SignUpSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    fname: str
    lname: str

class UpdateUserSchema(BaseModel):
    fname: Optional[str]
    lname: Optional[str]
    username: Optional[str]

class ViewUserSchema(UpdateUserSchema):
    email: EmailStr


""" User Settings Schema """
class UserSettingsSchema(BaseModel):
    auto_label : Optional[bool] = True
    auto_response : Optional[bool] = False
    create_draft : Optional[bool] = True
    schedule_event : Optional[bool] = False
    generate_report : Optional[bool] = False


""" User Labels Schema """
class UserLabelSchema(BaseModel):
    id: int
    label_name: Optional[str] = None
    label_description: Optional[str] = None