"""
Recommendations endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
import logging

from core.database import get_db
from core.security import get_current_user
from models.experiment import Experiment
from models.recommendation import Recommendation, RecommendationType, RecommendationPriority
from schemas.recommendation import RecommendationListResponse, RecommendationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{experiment_id}", response_model=RecommendationListResponse)
async def get_recommendations(
    experiment_id: UUID,
    segment: Optional[str] = Query(None),
    brand_goal: Optional[str] = Query(None),
    type: Optional[RecommendationType] = Query(None),
    priority: Optional[RecommendationPriority] = Query(None),
    min_impact_score: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recommendations for an experiment with optional filters
    """
    try:
        # Verify experiment exists and user has access
        exp_query = select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user["user_id"]
        )
        exp_result = await db.execute(exp_query)
        experiment = exp_result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
        
        # Build recommendations query
        query = select(Recommendation).where(Recommendation.experiment_id == experiment_id)
        
        # Apply filters
        filters_applied = {}
        
        if segment:
            query = query.where(Recommendation.segment == segment)
            filters_applied["segment"] = segment
        
        if brand_goal:
            query = query.where(Recommendation.brand_goal == brand_goal)
            filters_applied["brand_goal"] = brand_goal
        
        if type:
            query = query.where(Recommendation.type == type)
            filters_applied["type"] = type.value
        
        if priority:
            query = query.where(Recommendation.priority == priority)
            filters_applied["priority"] = priority.value
        
        if min_impact_score is not None:
            query = query.where(Recommendation.impact_score >= min_impact_score)
            filters_applied["min_impact_score"] = min_impact_score
        
        # Order by priority and impact score
        query = query.order_by(
            Recommendation.priority.desc(),
            Recommendation.impact_score.desc()
        )
        
        # Execute query
        result = await db.execute(query)
        recommendations = result.scalars().all()
        
        return RecommendationListResponse(
            recommendations=recommendations,
            total=len(recommendations),
            filtered_by=filters_applied
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )
