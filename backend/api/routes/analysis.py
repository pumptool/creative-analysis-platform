"""
Analysis endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
from datetime import datetime, timedelta

from core.database import get_db
from core.security import get_current_user
from models.experiment import Experiment, ExperimentStatus
from schemas.experiment import AnalysisStatusResponse, AnalysisTriggerResponse
from workers.tasks.analysis_tasks import analyze_experiment_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{experiment_id}/analyze", response_model=AnalysisTriggerResponse)
async def trigger_analysis(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger analysis pipeline for an experiment
    """
    try:
        # Get experiment
        query = select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user["user_id"]
        )
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
        
        # Check if already processing
        if experiment.status == ExperimentStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Experiment is already being processed"
            )
        
        # Check if required files are present
        if not experiment.video_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video URL is required"
            )
        
        if not experiment.results_csv_s3_key or not experiment.comments_csv_s3_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Results and comments CSV files are required"
            )
        
        # Update status
        experiment.status = ExperimentStatus.PROCESSING
        await db.commit()
        
        # Trigger Celery task
        task = analyze_experiment_task.delay(str(experiment_id))
        
        # Store task ID
        experiment.celery_task_id = task.id
        await db.commit()
        
        logger.info(f"Analysis triggered for experiment {experiment_id}, task ID: {task.id}")
        
        # Estimate completion time (5 minutes for typical video)
        estimated_completion = datetime.utcnow() + timedelta(minutes=5)
        
        return AnalysisTriggerResponse(
            task_id=task.id,
            status="processing",
            estimated_completion=estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger analysis: {str(e)}"
        )


@router.get("/{experiment_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current status of analysis pipeline
    """
    try:
        # Get experiment
        query = select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user["user_id"]
        )
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment not found"
            )
        
        # Get task status if available
        progress = {}
        estimated_completion = None
        
        if experiment.celery_task_id:
            from celery.result import AsyncResult
            task_result = AsyncResult(experiment.celery_task_id)
            
            if task_result.state == "PROGRESS":
                progress = task_result.info or {}
            elif task_result.state == "SUCCESS":
                progress = {
                    "video_analysis": "completed",
                    "quantitative_analysis": "completed",
                    "qualitative_analysis": "completed",
                    "recommendation_generation": "completed"
                }
            elif task_result.state == "FAILURE":
                progress = {"error": str(task_result.info)}
        
        return AnalysisStatusResponse(
            status=experiment.status,
            progress=progress,
            estimated_completion=estimated_completion,
            error_message=experiment.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis status: {str(e)}"
        )
