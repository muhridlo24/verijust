import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, Float, Integer, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
from app.db.base import Base  # Assuming you have a Base class

# Enums for strict typing
class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # SaaS Fields
    organization_name = Column(String, nullable=True)
    tier = Column(String, default=SubscriptionTier.FREE)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Rate Limiting & Quotas
    monthly_analysis_count = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="owner")
    audit_logs = relationship("ChainOfCustody", back_populates="actor")


class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    description = Column(Text)
    client_name = Column(String)
    case_number = Column(String) # Internal legal reference (e.g., "CASE-2026-001")
    
    status = Column(String, default="open") # open, closed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="cases")
    evidence_files = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    """
    Represents the actual raw file (Audio/Video).
    This is the central anchor for all forensic analysis.
    """
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False) # Secure path in AWS S3
    file_hash = Column(String, nullable=False) # SHA-256 Hash (CRITICAL for legal admissibility)
    file_size_bytes = Column(Integer)
    duration_seconds = Column(Float)
    mime_type = Column(String) # audio/mp3, audio/wav
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="evidence_files")
    analyses = relationship("Analysis", back_populates="evidence")
    chain_of_custody = relationship("ChainOfCustody", back_populates="evidence")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    
    # Model Configuration (Reproducibility)
    # We store WHICH model version was used (e.g., "nova-pro-v1", "whisper-large-v3")
    # If the model changes later, we know this report was generated with the old one.
    ai_model_config = Column(JSON) 
    
    status = Column(String, default="pending") # pending, processing, completed, failed
    
    # High-Level Metrics
    average_bluff_score = Column(Float) # 0.0 to 1.0 (Global score for the file)
    sentiment_distribution = Column(JSON) # {"angry": 0.4, "neutral": 0.6}
    speaker_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    evidence = relationship("Evidence", back_populates="analyses")
    segments = relationship("TranscriptSegment", back_populates="analysis", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """
    The atomic unit of the conversation.
    Used for: Vector Search, Diarization UI, and Bluff Flagging.
    """
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"))
    
    # Temporal Data (Where in the audio?)
    start_time = Column(Float, nullable=False) # e.g., 12.5s
    end_time = Column(Float, nullable=False)   # e.g., 15.2s
    
    # Content
    speaker_label = Column(String) # "Speaker 1" (Diarization result)
    text_content = Column(Text, nullable=False)
    
    # Micro-Analysis (Per-sentence intelligence)
    is_bluff = Column(Boolean, default=False)
    bluff_confidence = Column(Float) # How sure is the AI this is a lie?
    sentiment = Column(String) # "angry", "nervous", "neutral"
    
    # RAG Vector (1536 dimensions for Amazon Titan / OpenAI)
    embedding = Column(Vector(1536)) 

    analysis = relationship("Analysis", back_populates="segments")


class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    action = Column(String, nullable=False) 
    # Examples: "UPLOAD", "VIEW_REPORT", "DOWNLOAD_AUDIO", "DELETE"
    
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON) # {"old_status": "open", "new_status": "closed"}

    evidence = relationship("Evidence", back_populates="chain_of_custody")
    actor = relationship("User", back_populates="audit_logs")


class GuestToken(Base):
    __tablename__ = "guest_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    token = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)