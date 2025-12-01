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

# for the applications page
class ApplicationRead(BaseModel):
    application_id: int
    status: str
    date_applied: datetime
    job_title: str       # From Jobs table
    company_name: str    # From Employers table
    job_id: int

    class Config:
        from_attributes = True

# employer's application side
class ApplicationStatusUpdate(BaseModel):
    status: str

class EmployerApplicationRead(BaseModel):
    application_id: int
    applicant_name: str
    applicant_email: str
    job_title: str
    cover_letter: str
    resume_file: Optional[str]
    status: str
    date_applied: datetime

    class Config:
        from_attributes = True