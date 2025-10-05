"""
Celery tasks for experiment analysis
"""
from celery import Task
from workers.celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import tempfile
import os

from core.config import settings
from models.experiment import Experiment, ExperimentStatus
from models.video_analysis import VideoAnalysis
from models.recommendation import Recommendation, RecommendationType, RecommendationPriority
from integrations.twelvelabs_client import TwelveLabsClient
from integrations.twelvelabs_mock import MockTwelveLabsClient
from integrations.elevenlabs_client import ElevenLabsClient
from integrations.openai_client import OpenAIClient
from services.storage_service import StorageService
from utils.csv_parser import CSVParser
from utils.nlp_utils import NLPAnalyzer

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    """Base task with async support"""
    
    def __call__(self, *args, **kwargs):
        """Run async tasks in event loop"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run_async(*args, **kwargs))


@celery_app.task(bind=True, base=AsyncTask, name='analyze_experiment')
def analyze_experiment_task(self, experiment_id: str):
    """
    Main orchestration task for experiment analysis
    
    This task coordinates:
    1. Video analysis (TwelveLabs + ElevenLabs)
    2. Quantitative data analysis
    3. Qualitative data analysis (NLP)
    4. Recommendation generation
    """
    return asyncio.run(self.run_async(experiment_id))


async def run_async(self, experiment_id: str) -> Dict[str, Any]:
    """Async implementation of analysis task"""
    
    # Create async database session
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            logger.info(f"Starting analysis for experiment {experiment_id}")
            
            # Update status to processing
            experiment = await db.get(Experiment, experiment_id)
            if not experiment:
                raise Exception(f"Experiment {experiment_id} not found")
            
            experiment.status = ExperimentStatus.PROCESSING
            await db.commit()
            
            # Initialize services
            storage_service = StorageService()
            
            # Use mock client if USE_MOCK_APIS is set (for testing without API keys)
            use_mock = os.getenv("USE_MOCK_APIS", "false").lower() == "true"
            if use_mock:
                logger.warning("Using MOCK TwelveLabs client (no real API calls)")
                twelvelabs_client = MockTwelveLabsClient(settings.TWELVELABS_API_KEY)
            else:
                twelvelabs_client = TwelveLabsClient(settings.TWELVELABS_API_KEY)
            
            elevenlabs_client = ElevenLabsClient(settings.ELEVENLABS_API_KEY)
            openai_client = OpenAIClient(settings.OPENAI_API_KEY)
            nlp_analyzer = NLPAnalyzer()
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'step': 'video_analysis', 'progress': 0.1}
            )
            
            # Step 1: Video Analysis
            logger.info("Step 1: Analyzing video")
            video_data = await analyze_video(
                experiment,
                twelvelabs_client,
                elevenlabs_client,
                storage_service
            )
            
            # Save video analysis
            video_analysis = VideoAnalysis(
                experiment_id=experiment.id,
                video_id=video_data['video_id'],
                duration=video_data.get('duration', 0),
                creative_analysis=video_data.get('creative_analysis'),
                scenes=video_data.get('scenes'),
                transcript=video_data.get('transcript'),
                topics=video_data.get('topics'),
                key_moments=video_data.get('key_moments'),
                audio_analysis=video_data.get('audio_analysis'),
                model_version=settings.TWELVELABS_MODEL
            )
            db.add(video_analysis)
            await db.commit()
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'step': 'quantitative_analysis', 'progress': 0.4}
            )
            
            # Step 2: Quantitative Analysis
            logger.info("Step 2: Analyzing quantitative data")
            quant_data = await analyze_quantitative(
                experiment,
                storage_service
            )
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'step': 'qualitative_analysis', 'progress': 0.6}
            )
            
            # Step 3: Qualitative Analysis
            logger.info("Step 3: Analyzing qualitative data")
            qual_data = await analyze_qualitative(
                experiment,
                storage_service,
                nlp_analyzer,
                openai_client
            )
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'step': 'recommendation_generation', 'progress': 0.8}
            )
            
            # Step 4: Generate Recommendations
            logger.info("Step 4: Generating recommendations")
            recommendations = await generate_recommendations(
                experiment,
                video_data,
                quant_data,
                qual_data,
                openai_client
            )
            
            # Save recommendations
            for rec_data in recommendations:
                recommendation = Recommendation(
                    experiment_id=experiment.id,
                    segment=rec_data['segment'],
                    breakdown=rec_data.get('breakdown'),
                    brand_goal=rec_data['brand_goal'],
                    type=rec_data['type'],
                    priority=rec_data['priority'],
                    creative_element=rec_data['creative_element'],
                    justification=rec_data['justification'],
                    quantitative_support=rec_data.get('quantitative_support'),
                    qualitative_support=rec_data.get('qualitative_support'),
                    scene_reference=rec_data.get('scene_reference'),
                    impact_score=rec_data.get('impact_score'),
                    confidence_score=rec_data.get('confidence_score')
                )
                db.add(recommendation)
            
            await db.commit()
            
            # Update experiment summary
            summary = {
                'overall_favorability': quant_data.get('overall_favorability', 0),
                'overall_intent': quant_data.get('overall_intent', 0),
                'overall_associations': quant_data.get('overall_associations', 0),
                'recommendation_count': len(recommendations),
                'top_segment': quant_data.get('top_segment'),
                'weak_segment': quant_data.get('weak_segment')
            }
            
            experiment.summary = summary
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Analysis completed for experiment {experiment_id}")
            
            return {
                'experiment_id': experiment_id,
                'status': 'completed',
                'recommendations_count': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for experiment {experiment_id}: {e}")
            
            # Update experiment status to failed
            if experiment:
                experiment.status = ExperimentStatus.FAILED
                experiment.error_message = str(e)
                await db.commit()
            
            raise
        
        finally:
            await engine.dispose()


async def analyze_video(
    experiment: Experiment,
    twelvelabs_client: TwelveLabsClient,
    elevenlabs_client: ElevenLabsClient,
    storage_service: StorageService
) -> Dict[str, Any]:
    """Analyze video using TwelveLabs and ElevenLabs"""
    
    try:
        # Upload and index video
        video_url = experiment.video_url
        upload_result = twelvelabs_client.upload_video(
            video_url=video_url,
            video_title=experiment.title
        )
        
        video_id = upload_result['video_id']
        experiment.video_id = video_id
        
        # Get creative analysis
        creative_analysis = twelvelabs_client.analyze_creative_elements(video_id)
        
        # Get scene breakdown
        scenes = twelvelabs_client.get_video_segments(video_id)
        
        # Get key moments/highlights
        key_moments = twelvelabs_client.get_key_moments(video_id)
        
        # Audio analysis (if video file is available locally)
        audio_analysis = None
        try:
            # Download video temporarily for audio extraction
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
                if experiment.video_s3_key:
                    storage_service.download_file(experiment.video_s3_key, tmp_video.name)
                    
                    # Extract audio
                    audio_path = tmp_video.name.replace('.mp4', '_audio.mp3')
                    elevenlabs_client.extract_audio_from_video(tmp_video.name, audio_path)
                    
                    # Analyze audio
                    audio_analysis = elevenlabs_client.get_audio_insights(audio_path)
                    
                    # Cleanup
                    os.unlink(tmp_video.name)
                    os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
        
        return {
            'video_id': video_id,
            'duration': upload_result.get('duration'),
            'creative_analysis': creative_analysis.get('analysis'),
            'scenes': scenes,
            'key_moments': key_moments,
            'audio_analysis': audio_analysis
        }
        
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        raise


async def analyze_quantitative(
    experiment: Experiment,
    storage_service: StorageService
) -> Dict[str, Any]:
    """Analyze quantitative results CSV"""
    
    try:
        # Download CSV
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            storage_service.download_file(experiment.results_csv_s3_key, tmp_file.name)
            
            # Parse CSV
            df = CSVParser.parse_quantitative_results(tmp_file.name)
            
            # Calculate overall metrics
            overall_metrics = {}
            for metric in ['brand_favorability', 'purchase_intent', 'brand_associations']:
                metric_data = df[df['metric'] == metric]
                if not metric_data.empty:
                    # Weighted average delta
                    if 'totalWeight' in metric_data.columns:
                        overall_delta = (
                            metric_data['delta'] * metric_data['totalWeight']
                        ).sum() / metric_data['totalWeight'].sum()
                    else:
                        overall_delta = metric_data['delta'].mean()
                    
                    overall_metrics[metric] = overall_delta
            
            # Find top and weak segments
            segment_performance = df.groupby('segment')['delta'].mean().sort_values(ascending=False)
            top_segment = segment_performance.index[0] if len(segment_performance) > 0 else None
            weak_segment = segment_performance.index[-1] if len(segment_performance) > 0 else None
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            return {
                'overall_favorability': overall_metrics.get('brand_favorability', 0),
                'overall_intent': overall_metrics.get('purchase_intent', 0),
                'overall_associations': overall_metrics.get('brand_associations', 0),
                'top_segment': top_segment,
                'weak_segment': weak_segment,
                'dataframe': df  # Keep for recommendation generation
            }
            
    except Exception as e:
        logger.error(f"Quantitative analysis failed: {e}")
        raise


async def analyze_qualitative(
    experiment: Experiment,
    storage_service: StorageService,
    nlp_analyzer: NLPAnalyzer,
    openai_client: OpenAIClient
) -> Dict[str, Any]:
    """Analyze qualitative comments CSV"""
    
    try:
        # Download CSV
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            storage_service.download_file(experiment.comments_csv_s3_key, tmp_file.name)
            
            # Parse CSV
            df, response_cols = CSVParser.parse_qualitative_comments(tmp_file.name)
            
            # Analyze by segment
            segment_insights = {}
            
            # Get segment columns
            segment_cols = [col for col in df.columns if col not in ['response_id', 'treatment_group', 'weight'] + response_cols]
            
            for segment_col in segment_cols[:10]:  # Limit to top 10 segments
                # Get comments for this segment
                comments = CSVParser.get_comments_by_segment(df, response_cols[0], segment_col)
                
                if not comments:
                    continue
                
                # Sentiment analysis
                sentiment = nlp_analyzer.analyze_sentiment(comments)
                
                # Extract keywords
                keywords = nlp_analyzer.extract_keywords(comments, top_n=10)
                
                # Get representative comments
                rep_comments = nlp_analyzer.get_representative_comments(comments, limit=5)
                
                # Extract themes using OpenAI
                themes = openai_client.extract_themes_from_comments(comments, num_themes=3)
                
                segment_insights[segment_col] = {
                    'sentiment': sentiment,
                    'keywords': keywords,
                    'representative_comments': rep_comments,
                    'themes': themes,
                    'total_comments': len(comments)
                }
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            return {
                'segment_insights': segment_insights,
                'dataframe': df,
                'response_columns': response_cols
            }
            
    except Exception as e:
        logger.error(f"Qualitative analysis failed: {e}")
        raise


async def generate_recommendations(
    experiment: Experiment,
    video_data: Dict[str, Any],
    quant_data: Dict[str, Any],
    qual_data: Dict[str, Any],
    openai_client: OpenAIClient
) -> list[Dict[str, Any]]:
    """Generate creative recommendations"""
    
    recommendations = []
    
    try:
        df_quant = quant_data.get('dataframe')
        segment_insights = qual_data.get('segment_insights', {})
        
        # For each segment with negative performance
        for segment in segment_insights.keys():
            # Check quantitative performance
            for brand_goal in ['purchase_intent', 'brand_favorability', 'brand_associations']:
                segment_metrics = CSVParser.get_segment_metrics(df_quant, brand_goal, segment)
                
                if not segment_metrics or segment not in segment_metrics:
                    continue
                
                metrics = segment_metrics[segment]
                delta = metrics.get('delta', 0)
                
                # Generate recommendation if performance is negative
                if delta < -0.03:  # Threshold for negative impact
                    # Get qualitative themes
                    qual_insight = segment_insights.get(segment, {})
                    themes = [t.get('theme_label', '') for t in qual_insight.get('themes', [])]
                    
                    # Determine creative element to change
                    creative_element = determine_creative_element(video_data, qual_insight)
                    
                    # Generate justification
                    justification = openai_client.generate_recommendation_justification(
                        creative_element=creative_element,
                        quant_data={
                            'metric': brand_goal,
                            'delta': delta,
                            'ci_95': metrics.get('ci_95', [])
                        },
                        qual_themes=themes,
                        segment=segment
                    )
                    
                    # Determine recommendation type and priority
                    rec_type = RecommendationType.CHANGE if abs(delta) < 0.10 else RecommendationType.REMOVE
                    priority = RecommendationPriority.HIGH if abs(delta) > 0.08 else RecommendationPriority.MEDIUM
                    
                    recommendations.append({
                        'segment': segment,
                        'brand_goal': brand_goal,
                        'type': rec_type,
                        'priority': priority,
                        'creative_element': creative_element,
                        'justification': justification,
                        'quantitative_support': {
                            'metric': brand_goal,
                            'delta': delta,
                            'ci_95': metrics.get('ci_95'),
                            'baseline_mean': metrics.get('baseline_mean'),
                            'test_group_mean': metrics.get('test_group_mean'),
                            'statistical_significance': abs(delta) > metrics.get('margin_of_error', 0)
                        },
                        'qualitative_support': [
                            {'comment': c, 'theme': themes[0] if themes else None}
                            for c in qual_insight.get('representative_comments', [])[:3]
                        ],
                        'impact_score': abs(delta) * metrics.get('weight', 1.0),
                        'confidence_score': 1.0 - (metrics.get('margin_of_error', 0.1) / abs(delta) if delta != 0 else 0.5)
                    })
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        return []


def determine_creative_element(video_data: Dict[str, Any], qual_insight: Dict[str, Any]) -> str:
    """Determine which creative element to recommend changing"""
    
    # Extract keywords from qualitative feedback
    keywords = [kw['keyword'] for kw in qual_insight.get('keywords', [])[:5]]
    
    # Map keywords to creative elements
    if any(kw in ['voice', 'audio', 'music', 'sound'] for kw in keywords):
        return "Audio/voiceover tone"
    elif any(kw in ['color', 'visual', 'look', 'style'] for kw in keywords):
        return "Visual style and color palette"
    elif any(kw in ['message', 'text', 'copy', 'words'] for kw in keywords):
        return "Messaging and copy"
    elif any(kw in ['pace', 'fast', 'slow', 'editing'] for kw in keywords):
        return "Pacing and editing"
    else:
        return "Overall creative approach"


# Bind async method to task
analyze_experiment_task.run_async = run_async
