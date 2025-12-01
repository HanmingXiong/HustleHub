from pydantic import BaseModel
from typing import Optional

# What data we accept when updating a profile
class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

# What data we send back to the frontend
class ProfileResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    resume_file: Optional[str] = None
    
    class Config:
        from_attributes = True

# Change password
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
