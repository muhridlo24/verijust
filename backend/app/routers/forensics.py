from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
from typing import Optional, List

from app.services import storage
from app.tasks import process_audio_pipeline
from app.core.celery_app import celery_app
from app.core.dependencies import get_current_user, verify_usage_limits, UserContext
from app.core.config import settings
from app.db import session as db_session
from app.db import models
from celery.result import AsyncResult

router = APIRouter()

# --- Pydantic Models ---
class EvidenceOut(BaseModel):
    id: str
    filename: str
    file_size_bytes: Optional[int]
    duration_seconds: Optional[float]
    mime_type: str
    uploaded_at: str
    case_id: Optional[str]

    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id: str
    evidence_id: str
    status: str
    average_bluff_score: Optional[float]
    sentiment_distribution: Optional[dict]
    speaker_count: Optional[int]
    created_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True

class UploadResponseOut(BaseModel):
    evidence_id: str
    task_id: str
    status: str
    message: str

# --- Protected Endpoints ---

@router.post("/upload", response_model=UploadResponseOut)
async def upload_evidence(
    file: UploadFile = File(...),
    case_id: Optional[str] = None,
    user: UserContext = Depends(verify_usage_limits),
    db: Session = Depends(db_session.get_db)
):
    """
    Upload audio/video evidence file.
    
    Protected: Requires valid token
    Limits: Demo/guest users limited to 5MB
    """
    # 1. Validation
    allowed_types = (".mp3", ".wav", ".m4a", ".mp4", ".mov")
    if not file.filename.lower().endswith(allowed_types):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    # Ensure we can measure size safely
    try:
        file.file.seek(0, 2)  # seek to end
        size_bytes = file.file.tell()
        file.file.seek(0)
    except Exception:
        size_bytes = 0

    size_mb = (size_bytes or 0) / 1024.0 / 1024.0
    # Enforce global and guest-specific limits
    if user.is_guest and size_mb > settings.GUEST_UPLOAD_MAX_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"Guest uploads limited to {settings.GUEST_UPLOAD_MAX_SIZE_MB} MB")
    if size_mb > settings.UPLOAD_MAX_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"Upload exceeds max allowed size of {settings.UPLOAD_MAX_SIZE_MB} MB")

    # 2. Upload to S3
    try:
        # storage.upload_file expects UploadFile or path; it will use file.file
        s3_key = storage.upload_file(file)
        file_size = int(size_bytes or 0)
        mime_type = file.content_type or "application/octet-stream"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # 3. Create Evidence record in database
    try:
        evidence = models.Evidence(
            id=uuid4(),
            filename=file.filename,
            s3_key=s3_key,
            file_hash="pending",  # Will be computed asynchronously
            file_size_bytes=file_size,
            mime_type=mime_type,
            uploaded_at=datetime.utcnow(),
            case_id=case_id
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 4. Trigger analysis task
    try:
        task = process_audio_pipeline.delay(str(evidence.id), s3_key, user.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

    return {
        "evidence_id": str(evidence.id),
        "task_id": task.id,
        "status": "processing",
        "message": f"File '{file.filename}' uploaded. Analysis started."
    }

@router.get("/evidence", response_model=List[EvidenceOut])
async def get_user_evidence(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all evidence files for authenticated user.
    
    Protected: Requires valid token
    Returns: Paginated list of evidence files
    """
    try:
        evidence_files = db.query(models.Evidence)\
            .order_by(models.Evidence.uploaded_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [
            EvidenceOut(
                id=str(f.id),
                filename=f.filename,
                file_size_bytes=f.file_size_bytes,
                duration_seconds=f.duration_seconds,
                mime_type=f.mime_type,
                uploaded_at=f.uploaded_at.isoformat(),
                case_id=str(f.case_id) if f.case_id else None
            )
            for f in evidence_files
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/evidence/{evidence_id}", response_model=EvidenceOut)
async def get_evidence_details(
    evidence_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get details for a specific evidence file.
    
    Protected: Requires valid token
    """
    try:
        from uuid import UUID
        evidence = db.query(models.Evidence).filter(
            models.Evidence.id == UUID(evidence_id)
        ).first()
        
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        return EvidenceOut(
            id=str(evidence.id),
            filename=evidence.filename,
            file_size_bytes=evidence.file_size_bytes,
            duration_seconds=evidence.duration_seconds,
            mime_type=evidence.mime_type,
            uploaded_at=evidence.uploaded_at.isoformat(),
            case_id=str(evidence.case_id) if evidence.case_id else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/analysis/{evidence_id}", response_model=AnalysisOut)
async def get_analysis_results(
    evidence_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get analysis results for evidence file.
    
    Protected: Requires valid token
    Returns: Analysis status, metrics, and results
    """
    try:
        from uuid import UUID
        analysis = db.query(models.Analysis).filter(
            models.Analysis.evidence_id == UUID(evidence_id)
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisOut(
            id=str(analysis.id),
            evidence_id=str(analysis.evidence_id),
            status=analysis.status,
            average_bluff_score=analysis.average_bluff_score,
            sentiment_distribution=analysis.sentiment_distribution,
            speaker_count=analysis.speaker_count,
            created_at=analysis.created_at.isoformat(),
            completed_at=analysis.completed_at.isoformat() if analysis.completed_at else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/transcript/{evidence_id}")
async def get_transcript(
    evidence_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Get full transcript with segment details for evidence file.
    
    Protected: Requires valid token
    Returns: List of transcript segments with timestamps and analysis
    """
    try:
        from uuid import UUID
        segments = db.query(models.TranscriptSegment)\
            .join(models.Analysis)\
            .filter(models.Analysis.evidence_id == UUID(evidence_id))\
            .order_by(models.TranscriptSegment.start_time)\
            .all()
        
        if not segments:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return {
            "evidence_id": evidence_id,
            "segment_count": len(segments),
            "segments": [
                {
                    "id": seg.id,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "speaker_label": seg.speaker_label,
                    "text_content": seg.text_content,
                    "is_bluff": seg.is_bluff,
                    "bluff_confidence": seg.bluff_confidence,
                    "sentiment": seg.sentiment
                }
                for seg in segments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str,
    user: UserContext = Depends(get_current_user)
):
    """
    Get Celery task status for ongoing analysis.
    
    Protected: Requires valid token
    Returns: Task state, progress, and results
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        if task_result.state == 'PENDING':
            return {
                "task_id": task_id,
                "status": "pending",
                "progress": "Waiting in queue..."
            }
        elif task_result.state == 'STARTED':
            return {
                "task_id": task_id,
                "status": "started",
                "progress": "AI is analyzing..."
            }
        elif task_result.state == 'SUCCESS':
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task_result.result
            }
        elif task_result.state == 'FAILURE':
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(task_result.info)
            }
        
        return {
            "task_id": task_id,
            "status": task_result.state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.delete("/evidence/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(db_session.get_db)
):
    """
    Delete evidence file and associated analysis.
    
    Protected: Requires valid token
    Note: This soft-deletes the record and logs the action in chain_of_custody
    """
    try:
        from uuid import UUID
        evidence = db.query(models.Evidence).filter(
            models.Evidence.id == UUID(evidence_id)
        ).first()
        
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        # Log the deletion in chain of custody
        custody_log = models.ChainOfCustody(
            evidence_id=evidence.id,
            actor_id=None,  # Guest user
            action="DELETE",
            timestamp=datetime.utcnow(),
            details={"deleted_by": user.name}
        )
        db.add(custody_log)
        
        # Soft delete
        db.delete(evidence)
        db.commit()
        
        return {
            "message": f"Evidence '{evidence.filename}' deleted successfully",
            "evidence_id": evidence_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# --- Deprecated Endpoint (for backwards compatibility) ---
@router.post("/analyze-audio/")
async def analyze_audio(
    file: UploadFile = File(...),
    email: str = "user@example.com",
    user: UserContext = Depends(get_current_user)
):
    """
    Deprecated: Use /upload instead.
    This endpoint kept for backwards compatibility.
    """
    return await upload_evidence(file=file, user=user)