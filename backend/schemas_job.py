from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Public job card returned to lists/detail pages
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

# Incoming payload to create a job posting
class JobCreate(BaseModel):
    title: str
    description: str
    job_type: str
    location: str
    pay_range: Optional[str]

# Applicant submits cover letter when applying
class ApplicationCreate(BaseModel):
    cover_letter: str

# Applicant-facing view of their application status
class ApplicationRead(BaseModel):
    application_id: int
    status: str
    date_applied: datetime
    job_title: str
    company_name: str
    job_id: int

    class Config:
        from_attributes = True

# Employer updating an application's status
class ApplicationStatusUpdate(BaseModel):
    status: str

# Employer-facing view of applications to their job
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
