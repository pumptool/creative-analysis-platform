"""
Experiment management service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
from uuid import UUID

from models.experiment import Experiment, ExperimentStatus

logger = logging.getLogger(__name__)


class ExperimentService:
    """Service for managing experiments"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_experiment(
        self,
        title: str,
        user_id: str,
        description: Optional[str] = None
    ) -> Experiment:
        """
        Create a new experiment
        
        Args:
            title: Experiment title
            user_id: User ID
            description: Optional description
            
        Returns:
            Created experiment
        """
        try:
            experiment = Experiment(
                title=title,
                description=description,
                user_id=user_id,
                status=ExperimentStatus.PENDING
            )
            
            self.db.add(experiment)
            await self.db.commit()
            await self.db.refresh(experiment)
            
            logger.info(f"Experiment created: {experiment.id}")
            return experiment
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            await self.db.rollback()
            raise
    
    async def get_experiment(
        self,
        experiment_id: UUID,
        user_id: str
    ) -> Optional[Experiment]:
        """
        Get experiment by ID
        
        Args:
            experiment_id: Experiment ID
            user_id: User ID for authorization
            
        Returns:
            Experiment or None
        """
        try:
            query = select(Experiment).where(
                Experiment.id == experiment_id,
                Experiment.user_id == user_id
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get experiment: {e}")
            raise
    
    async def update_experiment_status(
        self,
        experiment_id: UUID,
        status: ExperimentStatus,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update experiment status
        
        Args:
            experiment_id: Experiment ID
            status: New status
            error_message: Optional error message
        """
        try:
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await self.db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if experiment:
                experiment.status = status
                if error_message:
                    experiment.error_message = error_message
                
                await self.db.commit()
                logger.info(f"Experiment {experiment_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update experiment status: {e}")
            await self.db.rollback()
            raise
    
    async def update_experiment_summary(
        self,
        experiment_id: UUID,
        summary: dict
    ) -> None:
        """
        Update experiment summary metrics
        
        Args:
            experiment_id: Experiment ID
            summary: Summary dictionary
        """
        try:
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await self.db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if experiment:
                experiment.summary = summary
                await self.db.commit()
                logger.info(f"Experiment {experiment_id} summary updated")
            
        except Exception as e:
            logger.error(f"Failed to update experiment summary: {e}")
            await self.db.rollback()
            raise
