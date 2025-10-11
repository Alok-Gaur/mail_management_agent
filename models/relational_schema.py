from pydantic import BaseModel, EmailStr
from typing import List, Optional

class SignUp(BaseModel):
    username: str
    email: EmailStr
    password: str
    fname: str
    lname: str

class ViewUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    fname: Optional[str]
    lname: Optional[str]

