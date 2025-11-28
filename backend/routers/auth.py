# routers/auth.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Users
from schemas_user import UserCreate, UserLogin, UserOut
from security import hash_password, verify_password, create_access_token
from jose import jwt, JWTError
from security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "hustlehub_access_token"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_token(request: Request, db: Session) -> Users:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_admin(user: Users):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")

# — REGISTRATION —
@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.email == user_in.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    existing_username = db.query(Users).filter(Users.username == user_in.username).first()
    if existing_username:
        raise HTTPException(400, "Username already taken")

    # Only allow applicant or employer during self-service registration
    selected_role = user_in.role or "applicant"
    if selected_role not in {"applicant", "employer"}:
        raise HTTPException(400, "Invalid role selection")

    user = Users(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=selected_role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# — LOGIN —
@router.post("/login", response_model=UserOut)
def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(400, "Invalid email or password")

    token = create_access_token({"sub": str(user.user_id)})

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # True in production
        max_age=60 * 60 * 24,
    )

    return user

# — LOGOUT —
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"detail": "Logged out"}

# — ME (user profile) —
@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    return get_user_from_token(request, db)

@router.get("/users", response_model=List[UserOut])
def list_users(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_token(request, db)
    require_admin(user)
    return db.query(Users).order_by(Users.user_id).all()
