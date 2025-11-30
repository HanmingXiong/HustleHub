# routers/jobs.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models
import schemas_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas_job.JobCard])
def read_jobs(db: Session = Depends(get_db)):
    # get jobs and employers of those jobs
    # only active jobs
    jobs_query = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Jobs.is_active == True)
        .order_by(models.Jobs.date_posted.desc())
        .all()
    )
    
    results = []
    for job in jobs_query:
        results.append(schemas_job.JobCard(
            job_id=job.job_id,
            employer_id=job.employer_id,
            company_name=job.employer.company_name, # Accessing the relationship from models.py
            title=job.title,
            description=job.description,
            job_type=job.job_type,
            location=job.location,
            pay_range=job.pay_range,
            date_posted=job.date_posted,
            is_active=job.is_active
        ))
        
    return results