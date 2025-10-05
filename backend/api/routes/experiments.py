"""
Experiment management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import logging
from uuid import UUID

from core.database import get_db
from core.security import get_current_user
from models.experiment import Experiment, ExperimentStatus
from schemas.experiment import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentListResponse,
    ExperimentUpdate
)
from services.storage_service import StorageService
from services.experiment_service import ExperimentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    results_csv: UploadFile = File(...),
    comments_csv: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)  # Temporarily disabled for demo
):
    """
    Create a new experiment with video and data files (authentication temporarily disabled)
    
    Either video_file or video_url must be provided
    """
    try:
        # Validate inputs
        if not video_file and not video_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either video_file or video_url must be provided"
            )
        
        # Create experiment service
        experiment_service = ExperimentService(db)
        storage_service = StorageService()
        
        # Create experiment record
        experiment = await experiment_service.create_experiment(
            title=title,
            description=description,
            user_id=current_user["user_id"]
        )
        
        # Upload files
        logger.info(f"Uploading files for experiment {experiment.id}")
        
        if video_file:
            video_s3_key = await storage_service.upload_video(
                file=video_file,
                experiment_id=str(experiment.id)
            )
            experiment.video_s3_key = video_s3_key
            experiment.video_url = storage_service.get_file_url(video_s3_key)
        else:
            experiment.video_url = video_url
        
        # Upload CSV files
        results_s3_key = await storage_service.upload_csv(
            file=results_csv,
            experiment_id=str(experiment.id),
            file_type="results"
        )
        experiment.results_csv_s3_key = results_s3_key
        
        comments_s3_key = await storage_service.upload_csv(
            file=comments_csv,
            experiment_id=str(experiment.id),
            file_type="comments"
        )
        experiment.comments_csv_s3_key = comments_s3_key
        
        # Update experiment
        await db.commit()
        await db.refresh(experiment)
        
        logger.info(f"Experiment {experiment.id} created successfully")
        
        return experiment
        
    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experiment: {str(e)}"
        )


@router.get("/", response_model=ExperimentListResponse)
async def list_experiments(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[ExperimentStatus] = None,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)  # Temporarily disabled for demo
):
    """
    List all experiments with pagination (authentication temporarily disabled)
    """
    try:
        # Build query - get all experiments (no user filter for demo)
        query = select(Experiment)
        # query = select(Experiment).where(Experiment.user_id == current_user["user_id"])
        
        if status_filter:
            query = query.where(Experiment.status == status_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # Apply pagination
        query = query.order_by(Experiment.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        experiments = result.scalars().all()
        
        # Calculate pages
        pages = (total + limit - 1) // limit
        
        return ExperimentListResponse(
            experiments=experiments,
            total=total,
            page=page,
            pages=pages,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list experiments: {str(e)}"
        )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific experiment by ID
    """
    try:
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
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experiment: {str(e)}"
        )


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: UUID,
    update_data: ExperimentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an experiment
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
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(experiment, field, value)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating experiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experiment: {str(e)}"
        )


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an experiment and all associated data
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
        
        # Delete from database (cascade will handle related records)
        await db.delete(experiment)
        await db.commit()
        
        logger.info(f"Experiment {experiment_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting experiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete experiment: {str(e)}"
        )
