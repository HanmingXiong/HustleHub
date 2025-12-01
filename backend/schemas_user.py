# schemas_user.py
from typing import Literal
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Literal["applicant", "employer"] = "applicant"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    user_id: int
    role: str

    class Config:
        from_attributes = True

class FinancialResourceCreate(BaseModel):
    website: str
    resource_type: Literal['credit', 'invest', 'budget']

    class Config:
        from_attributes = True

class FinancialResourceRead(BaseModel):
    resource_id: int
    website: str
    resource_type: str
    created_at: datetime

    class Config:
        from_attributes = True
