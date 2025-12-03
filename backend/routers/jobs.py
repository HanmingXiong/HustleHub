from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models
import schemas_job
from routers.auth import get_user_from_token

router = APIRouter(prefix="/jobs", tags=["jobs"])

def get_db():
    # Provide a DB session per request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas_job.JobCard])
def read_jobs(db: Session = Depends(get_db)):
    # Return active jobs enriched with employer info
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
            company_name=job.employer.company_name,
            title=job.title,
            description=job.description,
            job_type=job.job_type,
            location=job.location,
            pay_range=job.pay_range,
            date_posted=job.date_posted,
            is_active=job.is_active
        ))
        
    return results

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(job_data: schemas_job.JobCreate, 
               db: Session = Depends(get_db), 
               current_user: models.Users = Depends(get_user_from_token)):
    
    # Allow employers to create a new job posting
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can post jobs")

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

@router.get("/{job_id}", response_model=schemas_job.JobCard)
def read_job_detail(job_id: int, db: Session = Depends(get_db)):
    # Fetch a single job with employer info
    job = db.query(models.Jobs).join(models.Employers).filter(models.Jobs.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
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

    # Submit an application for a specific job
    # Block duplicate applications from the same user
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

@router.get("/applications/me", response_model=List[schemas_job.ApplicationRead])
def get_my_applications(
    db: Session = Depends(get_db), 
    current_user: models.Users = Depends(get_user_from_token)
):
    # Applicant view: list their submissions with job metadata
    applications = (
        db.query(
            models.Applications.application_id,
            models.Applications.status,
            models.Applications.date_applied,
            models.Applications.job_id,
            models.Jobs.title.label("job_title"),
            models.Employers.company_name.label("company_name")
        )
        .join(models.Jobs, models.Applications.job_id == models.Jobs.job_id)
        .join(models.Employers, models.Jobs.employer_id == models.Employers.employer_id)
        .filter(models.Applications.user_id == current_user.user_id)
        .order_by(models.Applications.date_applied.desc())
        .all()
    )

    return applications

@router.get("/employer/applications", response_model=List[schemas_job.EmployerApplicationRead])
def get_employer_applications(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Employer view: applications across jobs they own
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can access this")
        
    # Employer view: applications across jobs they own
    results = (
        db.query(
            models.Applications.application_id,
            models.Users.username.label("applicant_name"),
            models.Users.email.label("applicant_email"),
            models.Users.resume_file,
            models.Jobs.title.label("job_title"),
            models.Applications.cover_letter,
            models.Applications.status,
            models.Applications.date_applied
        )
        .join(models.Users, models.Applications.user_id == models.Users.user_id)
        .join(models.Jobs, models.Applications.job_id == models.Jobs.job_id)
        .join(models.Employers, models.Jobs.employer_id == models.Employers.employer_id)
        .filter(models.Employers.user_id == current_user.user_id)
        .order_by(models.Applications.date_applied.desc())
        .all()
    )

    return results

@router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    status_update: schemas_job.ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Allow employers to change an application's status
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can update status")

    valid_statuses = ["pending", "reviewed", "accepted", "rejected"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    application = db.query(models.Applications).filter(models.Applications.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Ensure the job belongs to the current employer before updating status
    job_ownership = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Jobs.job_id == application.job_id)
        .filter(models.Employers.user_id == current_user.user_id)
        .first()
    )

    if not job_ownership:
        raise HTTPException(status_code=403, detail="You are not authorized to manage this application")

    application.status = status_update.status
    db.commit()
    
    return {"message": "Status updated successfully", "status": application.status}
