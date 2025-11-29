from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import FinancialResources
from schemas_user import FinancialResourceRead

router = APIRouter(prefix="/financial-resources", tags=["Financial Resources"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{resource_type}", response_model=list[FinancialResourceRead])
def get_resources(resource_type: str, db: Session = Depends(get_db)):

    valid_types = {"credit", "budget", "invest"}
    if resource_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid resource type")

    return db.query(FinancialResources).filter(
        FinancialResources.resource_type == resource_type
    ).all()
