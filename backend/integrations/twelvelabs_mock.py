"""
Mock TwelveLabs client for testing without API key
Use this for demos or development when you don't have API access
"""
import time
import uuid
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MockTwelveLabsClient:
    """Mock client that simulates TwelveLabs API responses"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.index_id = "mock_index_123"
        logger.info("Using MOCK TwelveLabs client (no real API calls)")
        
    def create_or_get_index(self, index_name: str = "creative_pretest_index") -> str:
        """Mock index creation"""
        logger.info(f"MOCK: Created/retrieved index: {self.index_id}")
        return self.index_id
    
    def upload_video(self, video_url: str, video_title: str = None) -> Dict[str, Any]:
        """Mock video upload and indexing"""
        logger.info(f"MOCK: Uploading video: {video_url}")
        
        # Simulate processing time
        time.sleep(2)
        
        video_id = f"mock_video_{uuid.uuid4().hex[:8]}"
        
        return {
            "video_id": video_id,
            "status": "ready",
            "duration": 60.0
        }
    
    def analyze_creative_elements(self, video_id: str) -> Dict[str, Any]:
        """Mock creative analysis"""
        logger.info(f"MOCK: Analyzing video: {video_id}")
        
        # Simulate processing time
        time.sleep(1)
        
        mock_analysis = {
            "visual_elements": {
                "color_palette": ["blue", "white", "orange"],
                "visual_style": "Modern, minimalist with clean lines",
                "key_objects": ["smartphone", "laptop", "people smiling"],
                "settings": ["office", "outdoor park", "home interior"],
                "text_overlays": ["Introducing the future", "Available now"]
            },
            "pacing_and_editing": {
                "overall_pacing": "Fast-paced with quick cuts",
                "scene_transitions": 12,
                "editing_style": "Dynamic cuts with smooth transitions"
            },
            "audio_characteristics": {
                "music_genre": "Upbeat electronic",
                "music_mood": "Energetic and optimistic",
                "voiceover_tone": "Professional and confident",
                "sound_effects": "Minimal, subtle whooshes"
            },
            "messaging_and_tone": {
                "core_message": "Innovation meets simplicity",
                "emotional_tone": "Inspirational and aspirational",
                "brand_positioning": "Premium, tech-forward"
            },
            "key_moments": [
                {
                    "timestamp": 5.2,
                    "description": "Product reveal with dramatic lighting",
                    "importance": "high"
                },
                {
                    "timestamp": 15.8,
                    "description": "Customer testimonial begins",
                    "importance": "medium"
                },
                {
                    "timestamp": 45.0,
                    "description": "Call-to-action appears",
                    "importance": "high"
                }
            ]
        }
        
        return {
            "video_id": video_id,
            "analysis": mock_analysis,
            "model": "pegasus1.2"
        }
    
    def get_video_segments(self, video_id: str) -> List[Dict[str, Any]]:
        """Mock scene segmentation"""
        logger.info(f"MOCK: Getting segments for video: {video_id}")
        
        mock_scenes = [
            {
                "scene_id": "scene_1",
                "start_time": 0.0,
                "end_time": 8.5,
                "duration": 8.5,
                "description": "Opening shot: City skyline at dawn with dramatic music",
                "visual_tags": ["urban", "skyline", "sunrise", "aerial"],
                "transcript": "",
                "confidence": 0.95
            },
            {
                "scene_id": "scene_2",
                "start_time": 8.5,
                "end_time": 18.2,
                "duration": 9.7,
                "description": "Product showcase: Close-up of device with rotating camera",
                "visual_tags": ["product", "technology", "close-up", "rotating"],
                "transcript": "Introducing the future of innovation",
                "confidence": 0.92
            },
            {
                "scene_id": "scene_3",
                "start_time": 18.2,
                "end_time": 32.0,
                "duration": 13.8,
                "description": "Lifestyle montage: People using product in various settings",
                "visual_tags": ["people", "lifestyle", "happy", "diverse"],
                "transcript": "Designed for the way you live",
                "confidence": 0.89
            },
            {
                "scene_id": "scene_4",
                "start_time": 32.0,
                "end_time": 45.5,
                "duration": 13.5,
                "description": "Feature highlights: Split-screen showing key capabilities",
                "visual_tags": ["features", "split-screen", "graphics", "text"],
                "transcript": "Fast. Powerful. Intuitive.",
                "confidence": 0.91
            },
            {
                "scene_id": "scene_5",
                "start_time": 45.5,
                "end_time": 60.0,
                "duration": 14.5,
                "description": "Closing: Brand logo with call-to-action",
                "visual_tags": ["logo", "branding", "cta", "website"],
                "transcript": "Available now at example.com",
                "confidence": 0.94
            }
        ]
        
        return mock_scenes
    
    def search_video_content(self, video_id: str, query: str) -> List[Dict[str, Any]]:
        """Mock content search"""
        logger.info(f"MOCK: Searching for '{query}' in video: {video_id}")
        
        # Return mock matches based on query
        mock_matches = []
        
        if "product" in query.lower():
            mock_matches.append({
                "start_time": 8.5,
                "end_time": 18.2,
                "confidence": 0.92,
                "description": "Product showcase scene"
            })
        
        if "logo" in query.lower() or "brand" in query.lower():
            mock_matches.append({
                "start_time": 45.5,
                "end_time": 60.0,
                "confidence": 0.94,
                "description": "Brand logo display"
            })
        
        if "people" in query.lower():
            mock_matches.append({
                "start_time": 18.2,
                "end_time": 32.0,
                "confidence": 0.89,
                "description": "People using product"
            })
        
        return mock_matches
