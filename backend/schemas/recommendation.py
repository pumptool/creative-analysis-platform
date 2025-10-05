"""
Recommendation Pydantic schemas
"""
from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from models.recommendation import RecommendationType, RecommendationPriority


class QuantitativeSupport(BaseModel):
    """Quantitative evidence for recommendation"""
    metric: str
    delta: float
    ci_95: List[float]
    baseline_mean: Optional[float] = None
    test_group_mean: Optional[float] = None
    statistical_significance: bool


class QualitativeSupport(BaseModel):
    """Qualitative evidence for recommendation"""
    comment: str
    theme: Optional[str] = None
    sentiment: Optional[str] = None


class SceneReference(BaseModel):
    """Reference to video scene"""
    scene_id: str
    start_time: float
    end_time: float
    description: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    id: UUID4
    experiment_id: UUID4
    
    segment: str
    breakdown: Optional[str]
    brand_goal: str
    
    type: RecommendationType
    priority: RecommendationPriority
    creative_element: str
    justification: str
    
    quantitative_support: Optional[QuantitativeSupport]
    qualitative_support: Optional[List[QualitativeSupport]]
    scene_reference: Optional[SceneReference]
    
    impact_score: Optional[float]
    confidence_score: Optional[float]
    rank: Optional[int]
    
    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for filtered recommendation list"""
    recommendations: List[RecommendationResponse]
    total: int
    filtered_by: Dict[str, Any]


class RecommendationFilters(BaseModel):
    """Schema for recommendation filters"""
    segment: Optional[str] = None
    brand_goal: Optional[str] = None
    type: Optional[RecommendationType] = None
    priority: Optional[RecommendationPriority] = None
    min_impact_score: Optional[float] = None
