from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app.core.dependencies import get_current_user, UserContext
from app.db import session as db_session
from app.db import models

router = APIRouter()

# --- Pydantic Models ---
class UserProfileOut(BaseModel):
    id: str
    name: str
    full_name: Optional[str]
    email: Optional[str]
    is_guest: bool
    organization_name: Optional[str]
    tier: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

class CaseOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    client_name: Optional[str]
    case_number: Optional[str]
    status: str
    created_at: str

    class Config:
        from_attributes = True

class CreateCaseIn(BaseModel):
    title: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    case_number: Optional[str] = None

# --- Protected Endpoints ---

@router.get("/profile", response_model=UserProfileOut)
async def get_user_profile(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get authenticated user's profile.
    
    Protected: Requires valid token
    """
    try:
        # For guest users, return guest context
        if user.is_guest:
            return {
                "id": user.id,
                "name": user.name,
                "full_name": user.name,
                "email": None,
                "is_guest": True,
                "organization_name": None,
                "tier": "guest",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
        
        # For regular users, fetch from database
        from uuid import UUID
        db_user = db.query(models.User).filter(
            models.User.id == UUID(user.id)
        ).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(db_user.id),
            "name": db_user.full_name or "User",
            "full_name": db_user.full_name,
            "email": db_user.email,
            "is_guest": False,
            "organization_name": db_user.organization_name,
            "tier": db_user.tier,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/cases", response_model=list[CaseOut])
async def get_user_cases(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get all cases for authenticated user.
    
    Protected: Requires valid token
    """
    try:
        from uuid import UUID
        cases = db.query(models.Case).all()
        
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "description": c.description,
                "client_name": c.client_name,
                "case_number": c.case_number,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            }
            for c in cases
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/cases", response_model=CaseOut)
async def create_case(
    case_data: CreateCaseIn,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Create a new case.
    
    Protected: Requires valid token (guest users cannot create cases)
    """
    try:
        if user.is_guest:
            raise HTTPException(
                status_code=403,
                detail="Guest users cannot create cases"
            )
        
        from uuid import UUID
        new_case = models.Case(
            id=uuid4(),
            owner_id=UUID(user.id),
            title=case_data.title,
            description=case_data.description,
            client_name=case_data.client_name,
            case_number=case_data.case_number,
            status="open",
            created_at=datetime.utcnow()
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        
        return {
            "id": str(new_case.id),
            "title": new_case.title,
            "description": new_case.description,
            "client_name": new_case.client_name,
            "case_number": new_case.case_number,
            "status": new_case.status,
            "created_at": new_case.created_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Create failed: {str(e)}")

@router.get("/cases/{case_id}", response_model=CaseOut)
async def get_case_details(
    case_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get case details by ID.
    
    Protected: Requires valid token
    """
    try:
        from uuid import UUID
        case = db.query(models.Case).filter(
            models.Case.id == UUID(case_id)
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "id": str(case.id),
            "title": case.title,
            "description": case.description,
            "client_name": case.client_name,
            "case_number": case.case_number,
            "status": case.status,
            "created_at": case.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# --- Legacy endpoint for backwards compatibility ---
@router.post("/analyze")
async def start_analysis(
    file_url: str,
    user: UserContext = Depends(get_current_user)
):
    """
    Deprecated: Use /api/v1/forensics/upload instead.
    """
    if not file_url.startswith("s3://"):
        raise HTTPException(status_code=400, detail="Invalid S3 URL")

    return {"status": "success", "data": None}
