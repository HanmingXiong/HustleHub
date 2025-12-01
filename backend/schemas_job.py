from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# similar to the schemas_user.py
# used for job card definition

class JobCard(BaseModel):
    job_id: int
    employer_id: int
    company_name: str
    title: str
    description: str
    job_type: str
    location: str
    pay_range: Optional[str]
    date_posted: datetime
    is_active: bool

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    description: str
    job_type: str
    location: str
    pay_range: Optional[str]

class ApplicationCreate(BaseModel):
    cover_letter: str