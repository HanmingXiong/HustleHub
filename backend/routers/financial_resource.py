from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import FinancialResources, Users
from schemas_user import FinancialResourceRead, FinancialResourceCreate
from routers.auth import require_admin, get_user_from_token, get_db

router = APIRouter(prefix="/financial-literacy", tags=["Financial Resources"])

@router.get("/{resource_type}", response_model=list[FinancialResourceRead])
def get_resources(resource_type: str, db: Session = Depends(get_db)):

    valid_types = {"credit", "budget", "invest"}
    if resource_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid resource type")

    return db.query(FinancialResources).filter(
        FinancialResources.resource_type == resource_type
    ).all()

# @router.post("", response_model=None)
# def create_financial_resource(
#     resource_in: FinancialResourceCreate, 
#     db: Session = Depends(get_db),
#     token: Users = Depends(get_user_from_token),
# ):
#     require_admin(token) 

#     resource = FinancialResources(
#         website=resource_in.website,
#         resource_type=resource_in.resource_type,
#     )

#     db.add(resource)
#     db.commit()
#     db.refresh(resource)

#     return resource