from pydantic import BaseModel
from datetime import datetime

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
    pay_range: str | None
    date_posted: datetime
    is_active: bool

    class Config:
        from_attributes = True