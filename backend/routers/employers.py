from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users, Employers
from routers.auth import get_user_from_token
from pydantic import BaseModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/employers", tags=["employers"])

class EmployerCreate(BaseModel):
    company_name: str
    description: str | None = None
    website: str | None = None
    location: str | None = None

class EmployerResponse(BaseModel):
    employer_id: int
    user_id: int
    company_name: str
    description: str | None
    website: str | None
    location: str | None

    class Config:
        from_attributes = True

@router.get("/me", response_model=EmployerResponse)
def get_my_employer_info(
    current_user: Users = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can access this")
    
    employer = db.query(Employers).filter(Employers.user_id == current_user.user_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    
    return employer

@router.post("", response_model=EmployerResponse)
def create_employer_info(
    data: EmployerCreate,
    current_user: Users = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can create company profiles")
    
    # Check if employer already exists
    existing = db.query(Employers).filter(Employers.user_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employer profile already exists")
    
    employer = Employers(
        user_id=current_user.user_id,
        company_name=data.company_name,
        description=data.description,
        website=data.website,
        location=data.location
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return employer

@router.put("/me", response_model=EmployerResponse)
def update_employer_info(
    data: EmployerCreate,
    current_user: Users = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    if current_user.role != 'employer':
        raise HTTPException(status_code=403, detail="Only employers can update company profiles")
    
    employer = db.query(Employers).filter(Employers.user_id == current_user.user_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    
    employer.company_name = data.company_name
    employer.description = data.description
    employer.website = data.website
    employer.location = data.location
    
    db.commit()
    db.refresh(employer)
    return employer
