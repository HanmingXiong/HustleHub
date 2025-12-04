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
def read_jobs(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Return active jobs enriched with employer info and application status
    jobs_query = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Jobs.is_active == True)
        .order_by(models.Jobs.date_posted.desc())
        .all()
    )
    
    # Get user's applications
    user_applications = db.query(models.Applications.job_id).filter(
        models.Applications.user_id == current_user.user_id
    ).all()
    applied_job_ids = {app.job_id for app in user_applications}
    
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
            is_active=job.is_active,
            has_applied=job.job_id in applied_job_ids
        ))
        
    return results

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(job_data: schemas_job.JobCreate, 
               db: Session = Depends(get_db), 
               current_user: models.Users = Depends(get_user_from_token)):
    
    # Allow employers and admins to create a new job posting
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can post jobs")

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
    # Block employers from applying to jobs
    if current_user.role == 'employer':
        raise HTTPException(status_code=403, detail="Employers cannot apply to jobs")
    
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

@router.get("/employer/jobs", response_model=List[schemas_job.JobCard])
def get_employer_jobs(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Get all jobs posted by the employer (both active and inactive)
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can access this")
    
    employer_profile = db.query(models.Employers).filter(models.Employers.user_id == current_user.user_id).first()
    if not employer_profile:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    
    jobs = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Employers.employer_id == employer_profile.employer_id)
        .order_by(models.Jobs.date_posted.desc())
        .all()
    )
    
    results = []
    for job in jobs:
        # Count applications for this job
        application_count = db.query(models.Applications).filter(
            models.Applications.job_id == job.job_id
        ).count()
        
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
            is_active=job.is_active,
            application_count=application_count
        ))
    
    return results

@router.get("/employer/applications", response_model=List[schemas_job.EmployerApplicationRead])
def get_employer_applications(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Employer view: applications across jobs they own
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can access this")
        
    # Employer view: applications across jobs they own
    applications = (
        db.query(models.Applications, models.Users, models.Jobs)
        .join(models.Users, models.Applications.user_id == models.Users.user_id)
        .join(models.Jobs, models.Applications.job_id == models.Jobs.job_id)
        .join(models.Employers, models.Jobs.employer_id == models.Employers.employer_id)
        .filter(models.Employers.user_id == current_user.user_id)
        .order_by(models.Applications.date_applied.desc())
        .all()
    )

    results = []
    for app, user, job in applications:
        # Use full name if available, otherwise username
        if user.first_name and user.last_name:
            applicant_name = f"{user.first_name} {user.last_name}"
        elif user.first_name:
            applicant_name = user.first_name
        else:
            applicant_name = user.username
        
        results.append(schemas_job.EmployerApplicationRead(
            application_id=app.application_id,
            applicant_name=applicant_name,
            applicant_email=user.email,
            applicant_user_id=user.user_id,
            job_title=job.title,
            cover_letter=app.cover_letter,
            resume_file=user.resume_file,
            status=app.status,
            date_applied=app.date_applied
        ))

    return results

@router.get("/employer/applications/{job_id}", response_model=List[schemas_job.EmployerApplicationRead])
def get_employer_applications_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Employer view: applications for a specific job
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can access this")
    
    # Verify job ownership
    job = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Jobs.job_id == job_id)
        .filter(models.Employers.user_id == current_user.user_id)
        .first()
    )
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or you don't have permission")
    
    # Get applications for this specific job
    applications = (
        db.query(models.Applications, models.Users, models.Jobs)
        .join(models.Users, models.Applications.user_id == models.Users.user_id)
        .join(models.Jobs, models.Applications.job_id == models.Jobs.job_id)
        .filter(models.Applications.job_id == job_id)
        .order_by(models.Applications.date_applied.desc())
        .all()
    )

    results = []
    for app, user, job in applications:
        # Use full name if available, otherwise username
        if user.first_name and user.last_name:
            applicant_name = f"{user.first_name} {user.last_name}"
        elif user.first_name:
            applicant_name = user.first_name
        else:
            applicant_name = user.username
        
        results.append(schemas_job.EmployerApplicationRead(
            application_id=app.application_id,
            applicant_name=applicant_name,
            applicant_email=user.email,
            applicant_user_id=user.user_id,
            job_title=job.title,
            cover_letter=app.cover_letter,
            resume_file=user.resume_file,
            status=app.status,
            date_applied=app.date_applied
        ))

    return results

@router.put("/{job_id}/toggle-active")
def toggle_job_active(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Toggle job active status (only for job owner)
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can manage jobs")
    
    # Verify job ownership
    job = (
        db.query(models.Jobs)
        .join(models.Employers)
        .filter(models.Jobs.job_id == job_id)
        .filter(models.Employers.user_id == current_user.user_id)
        .first()
    )
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or you don't have permission")
    
    job.is_active = not job.is_active
    db.commit()
    
    return {"message": "Job status updated", "is_active": job.is_active}

@router.delete("/applications/withdraw/{job_id}")
def withdraw_application(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Allow applicants to withdraw their application
    application = db.query(models.Applications).filter(
        models.Applications.job_id == job_id,
        models.Applications.user_id == current_user.user_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application withdrawn successfully"}

@router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    status_update: schemas_job.ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_user_from_token)
):
    # Allow employers and admins to change an application's status
    if current_user.role not in ['employer', 'admin']:
        raise HTTPException(status_code=403, detail="Only employers and admins can update status")

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
