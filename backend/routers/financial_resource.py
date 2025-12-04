from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import FinancialResources, Users
from schemas_user import FinancialResourceRead, FinancialResourceCreate
from routers.auth import require_admin, get_user_from_token, get_db

router = APIRouter(prefix="/financial-literacy", tags=["Financial Resources"])

@router.get("/{resource_type}", response_model=list[FinancialResourceRead])
def get_resources(
    resource_type: str, 
    db: Session = Depends(get_db)
):
    # Fetch resources for a given category (credit/budget/invest)
    # No authentication required - public endpoint
    valid_types = {"credit", "budget", "invest"}
    if resource_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid resource type")

    resources = db.query(FinancialResources).filter(
        FinancialResources.resource_type == resource_type
    ).all()
    
    # Return resources with user_has_liked as false for unauthenticated users
    result = []
    for resource in resources:
        resource_dict = {
            "resource_id": resource.resource_id,
            "name": resource.name,
            "website": resource.website,
            "description": resource.description,
            "resource_type": resource.resource_type,
            "likes": resource.likes,
            "user_has_liked": False,  # Default to false for public access
            "created_at": resource.created_at
        }
        result.append(resource_dict)
    
    return result

@router.post("", response_model=None)
def create_financial_resource(
    resource_in: FinancialResourceCreate, 
    db: Session = Depends(get_db),
    token: Users = Depends(get_user_from_token),
):
    # Admin-only creation of financial resources
    require_admin(token) 

    resource = FinancialResources(
        name=resource_in.name,
        website=resource_in.website,
        description=resource_in.description,
        resource_type=resource_in.resource_type,
        likes=0
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource

@router.put("/{resource_id}", response_model=None)
def update_financial_resource(
    resource_id: int,
    resource_in: FinancialResourceCreate,
    db: Session = Depends(get_db),
    token: Users = Depends(get_user_from_token),
):
    # Admin-only update of financial resources
    require_admin(token)
    
    resource = db.query(FinancialResources).filter(
        FinancialResources.resource_id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.name = resource_in.name
    resource.website = resource_in.website
    resource.description = resource_in.description
    resource.resource_type = resource_in.resource_type
    
    db.commit()
    db.refresh(resource)
    
    return {"message": "Resource updated successfully"}

@router.delete("/{resource_id}")
def delete_financial_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    token: Users = Depends(get_user_from_token),
):
    # Admin-only deletion of financial resources
    require_admin(token)
    
    resource = db.query(FinancialResources).filter(
        FinancialResources.resource_id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    
    return {"message": "Resource deleted successfully"}

@router.post("/{resource_id}/like")
def like_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_user_from_token)
):
    # Check if resource exists
    resource = db.query(FinancialResources).filter(
        FinancialResources.resource_id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if user already liked this resource
    from models import ResourceLikes
    existing_like = db.query(ResourceLikes).filter(
        ResourceLikes.resource_id == resource_id,
        ResourceLikes.user_id == current_user.user_id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this resource")
    
    # Add like
    new_like = ResourceLikes(
        resource_id=resource_id,
        user_id=current_user.user_id
    )
    db.add(new_like)
    
    # Increment like count
    resource.likes += 1
    db.commit()
    
    return {"message": "Resource liked", "likes": resource.likes}

@router.delete("/{resource_id}/like")
def unlike_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_user_from_token)
):
    # Check if resource exists
    resource = db.query(FinancialResources).filter(
        FinancialResources.resource_id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if user has liked this resource
    from models import ResourceLikes
    existing_like = db.query(ResourceLikes).filter(
        ResourceLikes.resource_id == resource_id,
        ResourceLikes.user_id == current_user.user_id
    ).first()
    
    if not existing_like:
        raise HTTPException(status_code=400, detail="You haven't liked this resource")
    
    # Remove like
    db.delete(existing_like)
    
    # Decrement like count
    resource.likes = max(0, resource.likes - 1)
    db.commit()
    
    return {"message": "Like removed", "likes": resource.likes}
