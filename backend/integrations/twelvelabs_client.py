"""
TwelveLabs API client for video understanding
Based on official TwelveLabs Python SDK
"""
from twelvelabs import TwelveLabs
from twelvelabs.indexes import IndexesCreateRequestModelsItem
from twelvelabs.tasks import TasksRetrieveResponse
from typing import Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)


class TwelveLabsClient:
    """Client for TwelveLabs video analysis API"""
    
    def __init__(self, api_key: str):
        self.client = TwelveLabs(api_key=api_key)
        self.index_id = None
        
    def create_or_get_index(self, index_name: str = "creative_pretest_index") -> str:
        """Create a new index or retrieve existing one"""
        try:
            # Try to get existing index
            indexes = self.client.indexes.list()
            for index in indexes:
                if index.name == index_name:
                    self.index_id = index.id
                    logger.info(f"Using existing index: {self.index_id}")
                    return self.index_id
            
            # Create new index with Pegasus 1.2 model
            # Using visual and audio options for comprehensive analysis
            resp = self.client.indexes.create(
                index_name=index_name,
                models=[
                    IndexesCreateRequestModelsItem(
                        model_name="pegasus1.2",
                        model_options=["visual", "audio"]
                    )
                ]
            )
            self.index_id = resp.id
            logger.info(f"Created new index: id={self.index_id} name={index_name}")
            return self.index_id
            
        except Exception as e:
            logger.error(f"Error creating/getting index: {e}")
            raise
    
    def upload_video(self, video_url: str, video_title: str = None) -> Dict[str, Any]:
        """
        Upload video to TwelveLabs and wait for indexing to complete
        
        Args:
            video_url: URL to video file (S3, YouTube, etc.)
            video_title: Optional title for the video
            
        Returns:
            Dict with video_id and indexing status
        """
        try:
            if not self.index_id:
                self.create_or_get_index()
            
            # Create indexing task
            task = self.client.tasks.create(
                index_id=self.index_id,
                video_url=video_url
            )
            
            logger.info(f"Created task: id={task.id}")
            
            # Monitor the indexing process with callback
            def on_task_update(task: TasksRetrieveResponse):
                logger.info(f"  Indexing status={task.status}")
            
            # Wait for indexing to complete
            task = self.client.tasks.wait_for_done(
                task_id=task.id,
                sleep_interval=5,
                callback=on_task_update
            )
            
            if task.status != "ready":
                raise RuntimeError(f"Indexing failed with status {task.status}")
            
            logger.info(f"Upload complete. Video ID: {task.video_id}")
            
            return {
                "video_id": task.video_id,
                "status": task.status,
                "duration": getattr(task, "duration", None)
            }
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise
    
    def analyze_creative_elements(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze video for creative elements using TwelveLabs API
        
        Uses gist, summarize, and analyze endpoints to get comprehensive insights
        
        Returns detailed breakdown of:
        - Title, topics, hashtags (from gist)
        - Summary and chapters (from summarize)
        - Detailed analysis (from analyze_stream)
        """
        try:
            logger.info(f"Analyzing creative elements for video {video_id}")
            
            # 1. Get gist (title, topics, hashtags)
            gist = self.client.gist(
                video_id=video_id,
                types=["title", "topic", "hashtag"]
            )
            logger.info(f"Gist: Title={gist.title}")
            
            # 2. Get summary
            summary_result = self.client.summarize(
                video_id=video_id,
                type="summary"
            )
            
            # 3. Get chapters
            chapters_result = self.client.summarize(
                video_id=video_id,
                type="chapter"
            )
            
            # 4. Get highlights
            highlights_result = self.client.summarize(
                video_id=video_id,
                type="highlight"
            )
            
            # 5. Get detailed analysis using analyze_stream
            analysis_prompt = """Provide a detailed analysis of this advertisement including:
            - Visual style, color palette, and composition
            - Pacing and editing techniques
            - Audio characteristics (music, voiceover, sound effects)
            - Core messaging and emotional tone
            - Key moments and their impact
            - Overall creative effectiveness"""
            
            analysis_text = ""
            text_stream = self.client.analyze_stream(
                video_id=video_id,
                prompt=analysis_prompt
            )
            
            for text in text_stream:
                if text.event_type == "text_generation":
                    analysis_text += text.text
            
            # Combine all insights
            analysis_data = {
                "title": gist.title,
                "topics": gist.topics,
                "hashtags": gist.hashtags,
                "summary": summary_result.summary,
                "chapters": [
                    {
                        "chapter_number": ch.chapter_number,
                        "start_sec": ch.start_sec,
                        "end_sec": ch.end_sec,
                        "title": ch.chapter_title,
                        "summary": ch.chapter_summary
                    }
                    for ch in chapters_result.chapters
                ],
                "highlights": [
                    {
                        "highlight": h.highlight,
                        "start_sec": h.start_sec,
                        "end_sec": h.end_sec
                    }
                    for h in highlights_result.highlights
                ],
                "detailed_analysis": analysis_text
            }
            
            logger.info(f"Analysis complete for video {video_id}")
            
            return {
                "video_id": video_id,
                "analysis": analysis_data,
                "model": "pegasus1.2"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            raise
    
    def get_video_segments(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get scene-by-scene breakdown of video using chapters
        
        Returns list of scenes with:
        - Start/end timestamps
        - Scene description
        - Chapter title and summary
        """
        try:
            # Use summarize API with type="chapter" to get scene breakdown
            chapters_result = self.client.summarize(
                video_id=video_id,
                type="chapter"
            )
            
            scenes = []
            for chapter in chapters_result.chapters:
                scenes.append({
                    "scene_id": f"chapter_{chapter.chapter_number}",
                    "start_time": chapter.start_sec,
                    "end_time": chapter.end_sec,
                    "duration": chapter.end_sec - chapter.start_sec,
                    "description": chapter.chapter_summary,
                    "title": chapter.chapter_title,
                    "chapter_number": chapter.chapter_number,
                    "visual_tags": [],  # Not provided by chapters API
                    "transcript": "",  # Not provided by chapters API
                    "confidence": 1.0  # Chapters are always high confidence
                })
            
            logger.info(f"Retrieved {len(scenes)} scenes for video {video_id}")
            return scenes
            
        except Exception as e:
            logger.error(f"Error getting video segments: {e}")
            # Return empty list if segmentation fails
            return []
    
    def get_key_moments(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get key moments/highlights from the video
        
        Returns list of important moments with timestamps
        """
        try:
            highlights_result = self.client.summarize(
                video_id=video_id,
                type="highlight"
            )
            
            key_moments = []
            for highlight in highlights_result.highlights:
                key_moments.append({
                    "description": highlight.highlight,
                    "start_time": highlight.start_sec,
                    "end_time": highlight.end_sec,
                    "importance": "high"  # All highlights are considered important
                })
            
            logger.info(f"Retrieved {len(key_moments)} key moments for video {video_id}")
            return key_moments
            
        except Exception as e:
            logger.error(f"Error getting key moments: {e}")
            return []
