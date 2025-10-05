"""
Experiment Pydantic schemas
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime
from models.experiment import ExperimentStatus


class ExperimentCreate(BaseModel):
    """Schema for creating a new experiment"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ExperimentStatus] = None


class ExperimentSummary(BaseModel):
    """Summary metrics for an experiment"""
    overall_favorability: Optional[float] = None
    overall_intent: Optional[float] = None
    overall_associations: Optional[float] = None
    recommendation_count: int = 0
    top_segment: Optional[str] = None
    weak_segment: Optional[str] = None


class ExperimentResponse(BaseModel):
    """Schema for experiment response"""
    id: UUID4
    title: str
    description: Optional[str]
    status: ExperimentStatus
    error_message: Optional[str]
    
    video_url: Optional[str]
    video_id: Optional[str]
    
    summary: Optional[Dict[str, Any]]
    
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    user_id: str
    
    class Config:
        from_attributes = True


class ExperimentListResponse(BaseModel):
    """Schema for paginated experiment list"""
    experiments: list[ExperimentResponse]
    total: int
    page: int
    pages: int
    limit: int


class AnalysisStatusResponse(BaseModel):
    """Schema for analysis status"""
    status: ExperimentStatus
    progress: Dict[str, str]
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


class AnalysisTriggerResponse(BaseModel):
    """Schema for analysis trigger response"""
    task_id: str
    status: str
    estimated_completion: Optional[datetime] = None
