# routers/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models
import schemas_job
from routers.auth import get_user_from_token

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

# for creating a job posting, also send 201 created instead of 200 -> debugging purposes
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(job_data: schemas_job.JobCreate, 
               db: Session = Depends(get_db), 
               current_user: models.Users = Depends(get_user_from_token)):
    
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can post jobs")

    # find the employer profile associated with this user
    employer_profile = db.query(models.Employers).filter(models.Employers.user_id == current_user.user_id).first()
    
    if not employer_profile:
        raise HTTPException(status_code=400, detail="Employer profile not found. Please complete your profile first.")

    new_job = models.Jobs(
        employer_id=employer_profile.employer_id,
        title=job_data.title,
        description=job_data.description,
        job_type=job_data.job_type,
        location=job_data.location,
        pay_range=job_data.pay_range,
        is_active=True
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {"message": "Job created successfully", "job_id": new_job.job_id}

# for applications, need specfic job data
@router.get("/{job_id}", response_model=schemas_job.JobCard)
def read_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Jobs).join(models.Employers).filter(models.Jobs.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # map to schema
    return schemas_job.JobCard(
        job_id=job.job_id,
        employer_id=job.employer_id,
        company_name=job.employer.company_name,
        title=job.title,
        description=job.description,
        job_type=job.job_type,
        location=job.location,
        pay_range=job.pay_range,
        date_posted=job.date_posted,
        is_active=job.is_active
    )

@router.post("/{job_id}/apply", status_code=status.HTTP_201_CREATED)
def apply_for_job(job_id: int, 
                  application_data: schemas_job.ApplicationCreate, 
                  db: Session = Depends(get_db), 
                  current_user: models.Users = Depends(get_user_from_token)):

    # check if already applied
    existing_app = db.query(models.Applications).filter(
        models.Applications.job_id == job_id,
        models.Applications.user_id == current_user.user_id
    ).first()

    if existing_app:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    new_application = models.Applications(
        job_id=job_id,
        user_id=current_user.user_id,
        cover_letter=application_data.cover_letter,
        status='pending'
    )

    db.add(new_application)
    db.commit()
    return {"message": "Application submitted successfully"}