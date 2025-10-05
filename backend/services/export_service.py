"""
Export service for generating reports
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import logging
from uuid import UUID
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

from models.experiment import Experiment
from models.video_analysis import VideoAnalysis
from models.recommendation import Recommendation

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting experiment data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_to_json(self, experiment_id: UUID) -> Dict[str, Any]:
        """
        Export experiment data as JSON
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Complete experiment data as dictionary
        """
        try:
            # Get experiment
            experiment = await self.db.get(Experiment, experiment_id)
            if not experiment:
                raise ValueError("Experiment not found")
            
            # Get video analysis
            query = select(VideoAnalysis).where(VideoAnalysis.experiment_id == experiment_id)
            result = await self.db.execute(query)
            video_analysis = result.scalar_one_or_none()
            
            # Get recommendations
            query = select(Recommendation).where(Recommendation.experiment_id == experiment_id)
            result = await self.db.execute(query)
            recommendations = result.scalars().all()
            
            # Build export data
            export_data = {
                'experiment': {
                    'id': str(experiment.id),
                    'title': experiment.title,
                    'description': experiment.description,
                    'status': experiment.status.value,
                    'created_at': experiment.created_at.isoformat(),
                    'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
                    'summary': experiment.summary
                },
                'video_analysis': {
                    'video_id': video_analysis.video_id if video_analysis else None,
                    'duration': video_analysis.duration if video_analysis else None,
                    'creative_analysis': video_analysis.creative_analysis if video_analysis else None,
                    'scenes': video_analysis.scenes if video_analysis else [],
                    'audio_analysis': video_analysis.audio_analysis if video_analysis else None
                } if video_analysis else None,
                'recommendations': [
                    {
                        'id': str(rec.id),
                        'segment': rec.segment,
                        'brand_goal': rec.brand_goal,
                        'type': rec.type.value,
                        'priority': rec.priority.value,
                        'creative_element': rec.creative_element,
                        'justification': rec.justification,
                        'quantitative_support': rec.quantitative_support,
                        'qualitative_support': rec.qualitative_support,
                        'scene_reference': rec.scene_reference,
                        'impact_score': rec.impact_score,
                        'confidence_score': rec.confidence_score
                    }
                    for rec in recommendations
                ]
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise
    
    async def export_to_pdf(self, experiment_id: UUID) -> bytes:
        """
        Export experiment report as PDF
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            PDF file as bytes
        """
        try:
            # Get data
            data = await self.export_to_json(experiment_id)
            
            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph(
                f"<b>{data['experiment']['title']}</b>",
                styles['Title']
            )
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Executive Summary
            story.append(Paragraph("<b>Executive Summary</b>", styles['Heading1']))
            summary = data['experiment'].get('summary', {})
            summary_text = f"""
            Overall Brand Favorability: {summary.get('overall_favorability', 0):.2%}<br/>
            Overall Purchase Intent: {summary.get('overall_intent', 0):.2%}<br/>
            Total Recommendations: {summary.get('recommendation_count', 0)}<br/>
            Top Performing Segment: {summary.get('top_segment', 'N/A')}<br/>
            Weakest Segment: {summary.get('weak_segment', 'N/A')}
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Recommendations
            story.append(Paragraph("<b>Key Recommendations</b>", styles['Heading1']))
            
            for i, rec in enumerate(data['recommendations'][:10], 1):  # Top 10
                rec_title = Paragraph(
                    f"<b>{i}. {rec['creative_element']}</b> ({rec['segment']} - {rec['brand_goal']})",
                    styles['Heading2']
                )
                story.append(rec_title)
                
                rec_text = f"""
                <b>Type:</b> {rec['type']}<br/>
                <b>Priority:</b> {rec['priority']}<br/>
                <b>Justification:</b> {rec['justification']}<br/>
                <b>Impact Score:</b> {rec.get('impact_score', 0):.3f}
                """
                story.append(Paragraph(rec_text, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise
