"""
Export endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
import json
from io import BytesIO

from core.database import get_db
from core.security import get_current_user
from models.experiment import Experiment
from services.export_service import ExportService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{experiment_id}/json")
async def export_json(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export experiment data as JSON
    """
    try:
        # Verify experiment exists and user has access
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
        
        # Generate export
        export_service = ExportService(db)
        export_data = await export_service.export_to_json(experiment_id)
        
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename=experiment_{experiment_id}_export.json"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to JSON: {str(e)}"
        )


@router.get("/{experiment_id}/pdf")
async def export_pdf(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export experiment report as PDF
    """
    try:
        # Verify experiment exists and user has access
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
        
        # Generate PDF
        export_service = ExportService(db)
        pdf_bytes = await export_service.export_to_pdf(experiment_id)
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=experiment_{experiment.title.replace(' ', '_')}_report.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to PDF: {str(e)}"
        )
