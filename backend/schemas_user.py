from typing import Literal
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime

# Base shape for user-facing data
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

# Financial resource payloads
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
