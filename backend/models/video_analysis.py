"""
Video analysis database model
"""
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from core.database import Base


class VideoAnalysis(Base):
    """Video analysis results model"""
    __tablename__ = "video_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    # TwelveLabs data
    video_id = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)  # seconds
    
    # Creative analysis
    creative_analysis = Column(JSON, nullable=True)  # Structured analysis from TwelveLabs
    scenes = Column(JSON, nullable=True)  # List of scene objects
    transcript = Column(Text, nullable=True)  # Full video transcript
    topics = Column(JSON, nullable=True)  # List of detected topics
    key_moments = Column(JSON, nullable=True)  # Important timestamps
    
    # Audio analysis (from ElevenLabs)
    audio_analysis = Column(JSON, nullable=True)
    
    # Visual elements
    visual_tags = Column(JSON, nullable=True)  # List of visual elements detected
    color_palette = Column(JSON, nullable=True)  # Dominant colors
    
    # Metadata
    model_version = Column(String(50), nullable=True)
    processed_at = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<VideoAnalysis {self.id} for Experiment {self.experiment_id}>"
