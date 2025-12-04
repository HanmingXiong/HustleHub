from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import SessionLocal
from models import Users, Jobs, Employers
from routers.auth import get_user_from_token
from pydantic import BaseModel
from security import hash_password, verify_password

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(current_user: Users = Depends(get_user_from_token)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    first_name: str | None
    last_name: str | None
    phone: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

class PasswordVerify(BaseModel):
    password: str

class JobResponse(BaseModel):
    job_id: int
    employer_id: int
    company_name: str
    title: str
    description: str
    job_type: str
    location: str
    pay_range: str | None
    is_active: bool
    date_posted: datetime

    class Config:
        from_attributes = True

@router.post("/verify-password")
def verify_admin_password(
    password_data: PasswordVerify,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Verify the current admin's password
    is_valid = verify_password(password_data.password, admin.password_hash)
    return {"valid": is_valid}

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(Users).order_by(Users.created_at.desc()).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Check if username or email already exists
    existing = db.query(Users).filter(
        (Users.username == user_data.username) | (Users.email == user_data.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    if user_data.role not in ['applicant', 'employer', 'admin']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    new_user = Users(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == 'admin':
        raise HTTPException(status_code=403, detail="Cannot delete admin accounts")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/jobs", response_model=List[JobResponse])
def get_all_jobs(
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    jobs = (
        db.query(Jobs)
        .join(Employers)
        .order_by(Jobs.date_posted.desc())
        .all()
    )
    
    results = []
    for job in jobs:
        results.append(JobResponse(
            job_id=job.job_id,
            employer_id=job.employer_id,
            company_name=job.employer.company_name,
            title=job.title,
            description=job.description,
            job_type=job.job_type,
            location=job.location,
            pay_range=job.pay_range,
            is_active=job.is_active,
            date_posted=job.date_posted
        ))
    
    return results

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    admin: Users = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Jobs).filter(Jobs.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
