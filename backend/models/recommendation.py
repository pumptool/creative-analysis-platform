"""
Recommendation database model
"""
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from core.database import Base


class RecommendationType(str, enum.Enum):
    """Type of recommendation"""
    ADD = "add"
    CHANGE = "change"
    REMOVE = "remove"


class RecommendationPriority(str, enum.Enum):
    """Recommendation priority level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(Base):
    """Creative recommendation model"""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    # Segmentation
    segment = Column(String(255), nullable=False)
    breakdown = Column(String(255), nullable=True)
    brand_goal = Column(String(255), nullable=False)  # e.g., "purchase_intent", "brand_favorability"
    
    # Recommendation details
    type = Column(Enum(RecommendationType), nullable=False)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM)
    creative_element = Column(String(500), nullable=False)
    justification = Column(Text, nullable=False)
    
    # Supporting evidence
    quantitative_support = Column(JSON, nullable=True)  # Metrics, deltas, confidence intervals
    qualitative_support = Column(JSON, nullable=True)  # Representative comments
    
    # Video reference
    scene_reference = Column(JSON, nullable=True)  # Scene ID, timestamps
    
    # Impact scoring
    impact_score = Column(Float, nullable=True)  # Calculated impact potential
    confidence_score = Column(Float, nullable=True)  # Statistical confidence
    
    # Metadata
    rank = Column(Integer, nullable=True)  # Ranking within segment/goal
    
    def __repr__(self):
        return f"<Recommendation {self.id}: {self.type.value} {self.creative_element}>"
