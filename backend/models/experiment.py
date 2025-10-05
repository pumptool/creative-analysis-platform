"""
Experiment database model
"""
from sqlalchemy import Column, String, DateTime, Enum, Text, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from core.database import Base


class ExperimentStatus(str, enum.Enum):
    """Experiment processing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Experiment(Base):
    """Experiment model"""
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # File references
    video_url = Column(String(500), nullable=True)
    video_s3_key = Column(String(500), nullable=True)
    results_csv_s3_key = Column(String(500), nullable=True)
    comments_csv_s3_key = Column(String(500), nullable=True)
    
    # External IDs
    video_id = Column(String(255), nullable=True)  # TwelveLabs video ID
    celery_task_id = Column(String(255), nullable=True)
    
    # Summary metrics (cached for quick access)
    summary = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # User reference
    user_id = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<Experiment {self.id}: {self.title}>"
