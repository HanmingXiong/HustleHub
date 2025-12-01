from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from database import SessionLocal
from models import Users
from schemas_profile import ProfileUpdate, ProfileResponse, PasswordChange
from routers.auth import get_user_from_token
from security import verify_password, hash_password

router = APIRouter(prefix="/profile", tags=["profile"])

# Create uploads directory
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Users:
    return get_user_from_token(request, db)

# Get current user's profile
@router.get("/me", response_model=ProfileResponse)
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_token(request, db)
    return user

# Update profile
@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_user_from_token(request, db)
    
    # Update fields
    if profile_data.username:
        user.username = profile_data.username
    if profile_data.email:
        user.email = profile_data.email
    if profile_data.first_name is not None:
        user.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        user.last_name = profile_data.last_name
    if profile_data.phone is not None:
        user.phone = profile_data.phone
    
    db.commit()
    db.refresh(user)
    return user

# Upload resume (applicants only)
@router.post("/resume")
async def upload_resume(
    request: Request,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    user = get_user_from_token(request, db)
    
    if user.role != 'applicant':
        raise HTTPException(status_code=403, detail="Only applicants can upload resumes")
    
    # Check file type
    allowed = {'.pdf', '.doc', '.docx'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF, DOC, DOCX allowed")
    
    # Save file
    filename = f"resume_{user.user_id}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    # Delete old resume
    if user.resume_file and os.path.exists(user.resume_file):
        os.remove(user.resume_file)
    
    # Save new file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.resume_file = str(file_path)
    db.commit()
    db.refresh(user)
    
    return {"filename": filename, "resume_file": str(file_path)}

# Delete resume (applicants only)
@router.delete("/resume")
def delete_resume(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_token(request, db)
    
    if user.role != 'applicant':
        raise HTTPException(status_code=403, detail="Only applicants can delete resumes")
    
    if not user.resume_file:
        raise HTTPException(status_code=404, detail="No resume found")
    
    # Delete file
    if os.path.exists(user.resume_file):
        os.remove(user.resume_file)
    
    user.resume_file = None
    db.commit()
    
    return {"detail": "Resume deleted"}

# Change password
@router.put("/change-password")
def change_password(
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_user_from_token(request, db)
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    user.password_hash = hash_password(password_data.new_password)
    db.commit()
    
    return {"detail": "Password changed successfully"}
