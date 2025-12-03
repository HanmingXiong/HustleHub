from pydantic import BaseModel
from typing import Optional

# Incoming payload when a user edits their profile
class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

# Shape of profile data returned to clients
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

# Payload for password updates
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
