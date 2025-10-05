# API Integration Guide
## AI Creative Pre-testing Analysis Platform

**Version:** 1.0  
**Date:** October 4, 2025  
**Status:** Implementation Ready

---

## Table of Contents
1. [Overview](#overview)
2. [TwelveLabs Integration](#twelvelabs-integration)
3. [ElevenLabs Integration](#elevenlabs-integration)
4. [OpenAI Integration](#openai-integration)
5. [Internal API Specification](#internal-api-specification)
6. [Error Handling](#error-handling)
7. [Rate Limiting & Quotas](#rate-limiting--quotas)
8. [Testing & Validation](#testing--validation)

---

## Overview

### External APIs
| Service | Purpose | Pricing Tier | Rate Limit |
|---------|---------|--------------|------------|
| **TwelveLabs** | Video understanding (scenes, objects, transcripts) | Enterprise | 100 videos/day |
| **ElevenLabs** | Audio emotion analysis, voice characteristics | Pro | 1000 requests/day |
| **OpenAI GPT-4** | Qualitative summarization, insight generation | Pay-as-you-go | 10,000 tokens/min |

### Authentication
All API keys are stored in environment variables and managed via AWS Secrets Manager in production.

```python
# backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TWELVELABS_API_KEY: str
    ELEVENLABS_API_KEY: str
    OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## TwelveLabs Integration

### 1. Overview
TwelveLabs provides state-of-the-art video understanding through multimodal AI models. We use their **Pegasus 1.2** model with visual, audio, and conversation analysis.

**Documentation:** https://docs.twelvelabs.io/

### 2. Setup

#### 2.1 Installation
```bash
pip install twelvelabs-python
```

#### 2.2 Client Initialization
```python
# backend/integrations/twelvelabs_client.py
from twelvelabs import TwelveLabs
from twelvelabs.indexes import IndexesCreateRequestModelsItem
from twelvelabs.tasks import TasksRetrieveResponse
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TwelveLabsClient:
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
            
            # Create new index
            resp = self.client.indexes.create(
                index_name=index_name,
                models=[
                    IndexesCreateRequestModelsItem(
                        model_name="pegasus1.2",
                        model_options=["visual", "audio", "conversation"]
                    )
                ]
            )
            self.index_id = resp.id
            logger.info(f"Created new index: {self.index_id}")
            return self.index_id
            
        except Exception as e:
            logger.error(f"Error creating/getting index: {e}")
            raise
```

### 3. Core Operations

#### 3.1 Upload and Index Video
```python
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
            video_url=video_url,
            video_title=video_title or "Creative Pretest Video"
        )
        
        logger.info(f"Started indexing task: {task.id}")
        
        # Wait for indexing to complete (with timeout)
        task = self.client.tasks.wait_for_done(
            task_id=task.id,
            sleep_interval=5,  # Check every 5 seconds
            timeout=600  # 10 minute timeout
        )
        
        if task.status != "ready":
            raise Exception(f"Indexing failed with status: {task.status}")
        
        logger.info(f"Video indexed successfully: {task.video_id}")
        
        return {
            "video_id": task.video_id,
            "status": task.status,
            "duration": task.duration
        }
        
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise
```

#### 3.2 Generate Creative Analysis
```python
def analyze_creative_elements(self, video_id: str) -> Dict[str, Any]:
    """
    Analyze video for creative elements using custom prompt
    
    Returns detailed breakdown of:
    - Visual style and composition
    - Pacing and editing
    - Audio/music characteristics
    - Messaging and tone
    - Key moments and scenes
    """
    prompt = """
    Analyze this advertisement creative and provide:
    
    1. VISUAL ELEMENTS:
       - Color palette and visual style
       - Key objects, people, and settings shown
       - Camera angles and shot composition
       - Text overlays and graphics
    
    2. PACING & EDITING:
       - Overall pacing (fast/slow/varied)
       - Number of scene transitions
       - Editing style (cuts, fades, etc.)
    
    3. AUDIO CHARACTERISTICS:
       - Music genre and mood
       - Voiceover tone and style
       - Sound effects usage
    
    4. MESSAGING & TONE:
       - Core message or value proposition
       - Emotional tone (inspirational, humorous, serious, etc.)
       - Brand positioning
    
    5. KEY MOMENTS:
       - Most impactful scenes (with timestamps)
       - Product/brand reveal timing
       - Call-to-action placement
    
    Format as structured JSON.
    """
    
    try:
        result = self.client.generate.text(
            video_id=video_id,
            prompt=prompt
        )
        
        return {
            "video_id": video_id,
            "analysis": result.data,
            "model": "pegasus1.2"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        raise
```

#### 3.3 Get Scene-Level Breakdown
```python
def get_video_segments(self, video_id: str) -> List[Dict[str, Any]]:
    """
    Get scene-by-scene breakdown of video
    
    Returns list of scenes with:
    - Start/end timestamps
    - Scene description
    - Visual tags
    - Transcript (if dialogue present)
    """
    try:
        # Use the Classify API to segment video
        segments = self.client.classify.segments(
            video_id=video_id,
            options={
                "type": "visual",
                "include_transcript": True
            }
        )
        
        scenes = []
        for segment in segments:
            scenes.append({
                "scene_id": segment.id,
                "start_time": segment.start,
                "end_time": segment.end,
                "duration": segment.end - segment.start,
                "description": segment.metadata.get("description", ""),
                "visual_tags": segment.metadata.get("tags", []),
                "transcript": segment.metadata.get("transcript", ""),
                "confidence": segment.confidence
            })
        
        return scenes
        
    except Exception as e:
        logger.error(f"Error getting video segments: {e}")
        raise
```

#### 3.4 Search Within Video
```python
def search_video_content(self, video_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Search for specific content within video
    
    Example queries:
    - "product demonstration"
    - "people smiling"
    - "fast-paced editing"
    """
    try:
        results = self.client.search.query(
            index_id=self.index_id,
            query=query,
            options={
                "filter": {"video_id": video_id},
                "threshold": 0.7
            }
        )
        
        matches = []
        for result in results:
            matches.append({
                "start_time": result.start,
                "end_time": result.end,
                "confidence": result.confidence,
                "description": result.metadata.get("description", "")
            })
        
        return matches
        
    except Exception as e:
        logger.error(f"Error searching video: {e}")
        raise
```

### 4. Complete Integration Example
```python
# backend/services/video_service.py
from integrations.twelvelabs_client import TwelveLabsClient
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class VideoAnalysisService:
    def __init__(self):
        self.client = TwelveLabsClient(api_key=settings.TWELVELABS_API_KEY)
    
    async def analyze_video(self, video_url: str, experiment_id: str) -> Dict[str, Any]:
        """
        Complete video analysis pipeline
        """
        try:
            # 1. Upload and index video
            logger.info(f"Uploading video for experiment {experiment_id}")
            upload_result = self.client.upload_video(
                video_url=video_url,
                video_title=f"Experiment_{experiment_id}"
            )
            video_id = upload_result["video_id"]
            
            # 2. Get creative analysis
            logger.info(f"Analyzing creative elements for video {video_id}")
            creative_analysis = self.client.analyze_creative_elements(video_id)
            
            # 3. Get scene breakdown
            logger.info(f"Getting scene breakdown for video {video_id}")
            scenes = self.client.get_video_segments(video_id)
            
            # 4. Search for specific elements
            key_moments = []
            search_queries = [
                "product showcase",
                "people interacting",
                "brand logo",
                "call to action"
            ]
            
            for query in search_queries:
                matches = self.client.search_video_content(video_id, query)
                if matches:
                    key_moments.append({
                        "element": query,
                        "occurrences": matches
                    })
            
            # 5. Combine all insights
            return {
                "video_id": video_id,
                "duration": upload_result["duration"],
                "creative_analysis": creative_analysis["analysis"],
                "scenes": scenes,
                "key_moments": key_moments,
                "indexed_at": upload_result.get("indexed_at")
            }
            
        except Exception as e:
            logger.error(f"Video analysis failed for experiment {experiment_id}: {e}")
            raise
```

---

## ElevenLabs Integration

### 1. Overview
ElevenLabs provides advanced audio analysis capabilities, including voice emotion detection and audio quality assessment.

**Documentation:** https://elevenlabs.io/docs

### 2. Setup

```python
# backend/integrations/elevenlabs_client.py
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
```

### 3. Audio Analysis Operations

#### 3.1 Extract Audio from Video
```python
def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
    """
    Extract audio track from video file
    Uses ffmpeg under the hood
    """
    import subprocess
    
    try:
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-q:a", "2",  # High quality
            output_path
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"Audio extracted to {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Audio extraction failed: {e}")
        raise
```

#### 3.2 Analyze Voice Characteristics
```python
def analyze_voice_emotion(self, audio_file_path: str) -> Dict[str, Any]:
    """
    Analyze emotional characteristics of voice in audio
    
    Returns:
    - Dominant emotion
    - Emotion distribution
    - Voice characteristics (pitch, pace, energy)
    """
    try:
        # Note: This is a conceptual implementation
        # Actual ElevenLabs API endpoints may differ
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            
            response = requests.post(
                f"{self.base_url}/audio-analysis/emotion",
                headers={"xi-api-key": self.api_key},
                files=files
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "dominant_emotion": result.get("dominant_emotion"),
                "emotion_scores": result.get("emotions", {}),
                "voice_characteristics": {
                    "pitch": result.get("pitch"),
                    "pace": result.get("pace"),
                    "energy": result.get("energy"),
                    "clarity": result.get("clarity")
                }
            }
            
    except Exception as e:
        logger.error(f"Voice emotion analysis failed: {e}")
        raise
```

#### 3.3 Analyze Audio Quality
```python
def analyze_audio_quality(self, audio_file_path: str) -> Dict[str, Any]:
    """
    Assess technical quality of audio
    
    Returns:
    - Audio clarity score
    - Background noise level
    - Volume consistency
    """
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            
            response = requests.post(
                f"{self.base_url}/audio-analysis/quality",
                headers={"xi-api-key": self.api_key},
                files=files
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "clarity_score": result.get("clarity_score"),
                "noise_level": result.get("noise_level"),
                "volume_consistency": result.get("volume_consistency"),
                "overall_quality": result.get("overall_quality")
            }
            
    except Exception as e:
        logger.error(f"Audio quality analysis failed: {e}")
        raise
```

### 4. Integration with Video Analysis
```python
# backend/services/audio_service.py
from integrations.elevenlabs_client import ElevenLabsClient
from core.config import settings

class AudioAnalysisService:
    def __init__(self):
        self.client = ElevenLabsClient(api_key=settings.ELEVENLABS_API_KEY)
    
    async def analyze_video_audio(self, video_path: str) -> Dict[str, Any]:
        """
        Complete audio analysis for video creative
        """
        try:
            # 1. Extract audio
            audio_path = video_path.replace(".mp4", "_audio.mp3")
            self.client.extract_audio_from_video(video_path, audio_path)
            
            # 2. Analyze voice emotion
            emotion_analysis = self.client.analyze_voice_emotion(audio_path)
            
            # 3. Analyze audio quality
            quality_analysis = self.client.analyze_audio_quality(audio_path)
            
            # 4. Combine insights
            return {
                "emotion_analysis": emotion_analysis,
                "quality_analysis": quality_analysis,
                "recommendations": self._generate_audio_recommendations(
                    emotion_analysis, quality_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise
    
    def _generate_audio_recommendations(
        self, 
        emotion: Dict, 
        quality: Dict
    ) -> List[str]:
        """Generate audio-specific recommendations"""
        recommendations = []
        
        # Check emotion alignment
        if emotion["dominant_emotion"] in ["sad", "angry"]:
            recommendations.append(
                "Consider adjusting voiceover tone to be more positive/uplifting"
            )
        
        # Check quality issues
        if quality["clarity_score"] < 0.7:
            recommendations.append(
                "Audio clarity is below optimal - consider re-recording voiceover"
            )
        
        if quality["noise_level"] > 0.3:
            recommendations.append(
                "Background noise detected - apply noise reduction in post-production"
            )
        
        return recommendations
```

---

## OpenAI Integration

### 1. Overview
OpenAI GPT-4 is used for:
- Summarizing qualitative feedback
- Generating insight narratives
- Creating presentation-ready recommendation text

### 2. Setup

```python
# backend/integrations/openai_client.py
from openai import OpenAI
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
```

### 3. Core Operations

#### 3.1 Summarize Qualitative Comments
```python
def summarize_comments(
    self, 
    comments: List[str], 
    segment: str,
    max_length: int = 200
) -> str:
    """
    Generate concise summary of qualitative comments for a segment
    """
    try:
        prompt = f"""
        Summarize the following audience feedback for the "{segment}" segment.
        Focus on:
        1. Common themes
        2. Emotional reactions
        3. Specific creative elements mentioned
        
        Comments:
        {chr(10).join(f"- {c}" for c in comments[:50])}  # Limit to 50 comments
        
        Provide a concise summary in {max_length} words or less.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a marketing insights analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Comment summarization failed: {e}")
        raise
```

#### 3.2 Generate Recommendation Justification
```python
def generate_recommendation_justification(
    self,
    creative_element: str,
    quant_data: Dict[str, Any],
    qual_themes: List[str],
    segment: str
) -> str:
    """
    Generate clear, actionable justification for a recommendation
    """
    try:
        prompt = f"""
        Generate a concise justification for the following creative recommendation:
        
        Segment: {segment}
        Creative Element: {creative_element}
        
        Quantitative Evidence:
        - Metric: {quant_data['metric']}
        - Impact: {quant_data['delta']:.2%} change
        - Confidence: {quant_data['ci_95']}
        
        Qualitative Themes:
        {chr(10).join(f"- {theme}" for theme in qual_themes)}
        
        Write a 2-3 sentence justification that:
        1. States the problem clearly
        2. References both data sources
        3. Explains why this change will improve performance
        
        Use professional but accessible language for marketing stakeholders.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative strategy consultant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Justification generation failed: {e}")
        raise
```

#### 3.3 Generate Executive Summary
```python
def generate_executive_summary(
    self,
    experiment_data: Dict[str, Any]
) -> str:
    """
    Create executive summary for experiment results
    """
    try:
        prompt = f"""
        Create an executive summary for this creative pre-testing experiment:
        
        Video: {experiment_data['title']}
        
        Key Findings:
        - Overall brand favorability: {experiment_data['overall_favorability']:.2%}
        - Overall purchase intent: {experiment_data['overall_intent']:.2%}
        - Top performing segment: {experiment_data['top_segment']}
        - Weakest performing segment: {experiment_data['weak_segment']}
        
        Top 3 Recommendations:
        {chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(experiment_data['top_recommendations']))}
        
        Write a 150-word executive summary suitable for C-suite presentation.
        Include:
        1. Overall performance assessment
        2. Key opportunities
        3. Recommended next steps
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a marketing executive."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.4
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Executive summary generation failed: {e}")
        raise
```

---

## Internal API Specification

### Base URL
```
Development: http://localhost:8000/api
Production: https://api.creativeinsights.com/api
```

### Authentication
```http
Authorization: Bearer <JWT_TOKEN>
```

### Endpoints

#### 1. Experiments

##### Create Experiment
```http
POST /api/experiments
Content-Type: multipart/form-data

{
  "title": "Q4 Brand Campaign Test",
  "video_file": <file>,
  "results_csv": <file>,
  "comments_csv": <file>
}

Response 201:
{
  "id": "uuid",
  "title": "Q4 Brand Campaign Test",
  "status": "pending",
  "created_at": "2025-10-04T19:27:59Z"
}
```

##### List Experiments
```http
GET /api/experiments?page=1&limit=20

Response 200:
{
  "experiments": [
    {
      "id": "uuid",
      "title": "Q4 Brand Campaign Test",
      "status": "completed",
      "created_at": "2025-10-04T19:27:59Z",
      "summary": {
        "overall_favorability": 0.12,
        "overall_intent": 0.08,
        "recommendation_count": 15
      }
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

##### Get Experiment Details
```http
GET /api/experiments/{id}

Response 200:
{
  "id": "uuid",
  "title": "Q4 Brand Campaign Test",
  "status": "completed",
  "video_url": "https://...",
  "video_id": "twelvelabs_video_id",
  "created_at": "2025-10-04T19:27:59Z",
  "completed_at": "2025-10-04T19:32:15Z"
}
```

#### 2. Analysis

##### Trigger Analysis
```http
POST /api/experiments/{id}/analyze

Response 202:
{
  "task_id": "celery_task_id",
  "status": "processing",
  "estimated_completion": "2025-10-04T19:32:00Z"
}
```

##### Check Analysis Status
```http
GET /api/experiments/{id}/status

Response 200:
{
  "status": "processing",
  "progress": {
    "video_analysis": "completed",
    "quantitative_analysis": "completed",
    "qualitative_analysis": "in_progress",
    "recommendation_generation": "pending"
  },
  "estimated_completion": "2025-10-04T19:32:00Z"
}
```

##### Get Video Analysis
```http
GET /api/experiments/{id}/video-analysis

Response 200:
{
  "video_id": "twelvelabs_id",
  "duration": 60.5,
  "scenes": [
    {
      "scene_id": "1",
      "start_time": 0.0,
      "end_time": 5.2,
      "description": "Opening shot of city skyline",
      "visual_tags": ["urban", "modern", "aerial"],
      "transcript": ""
    }
  ],
  "creative_analysis": {
    "visual_style": "Modern, high-energy",
    "pacing": "Fast",
    "tone": "Inspirational"
  },
  "audio_analysis": {
    "dominant_emotion": "confident",
    "quality_score": 0.92
  }
}
```

##### Get Recommendations
```http
GET /api/experiments/{id}/recommendations?segment=age_18_24&brand_goal=purchase_intent

Response 200:
{
  "recommendations": [
    {
      "id": "uuid",
      "segment": "age_18_24",
      "brand_goal": "purchase_intent",
      "type": "change",
      "priority": "high",
      "creative_element": "Voiceover tone in opening scene",
      "justification": "Young adults found the formal tone disconnected...",
      "quantitative_support": {
        "metric": "purchase_intent",
        "delta": -0.08,
        "ci_95": [-0.12, -0.04],
        "statistical_significance": true
      },
      "qualitative_support": [
        {
          "comment": "The voiceover felt too corporate",
          "theme": "authenticity"
        }
      ],
      "scene_reference": {
        "scene_id": "1",
        "start_time": 0.0,
        "end_time": 5.2
      }
    }
  ],
  "total": 8,
  "filtered_by": {
    "segment": "age_18_24",
    "brand_goal": "purchase_intent"
  }
}
```

#### 3. Export

##### Export as JSON
```http
GET /api/experiments/{id}/export/json

Response 200:
{
  "experiment": {...},
  "video_analysis": {...},
  "metrics": {...},
  "qualitative_insights": {...},
  "recommendations": [...]
}
```

##### Export as PDF
```http
GET /api/experiments/{id}/export/pdf

Response 200:
Content-Type: application/pdf
Content-Disposition: attachment; filename="experiment_report.pdf"

<PDF binary data>
```

---

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VIDEO_INDEXING_FAILED",
    "message": "Failed to index video with TwelveLabs API",
    "details": {
      "video_url": "https://...",
      "twelvelabs_error": "Invalid video format"
    },
    "timestamp": "2025-10-04T19:27:59Z"
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request data |
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VIDEO_UPLOAD_FAILED` | 500 | Video upload to S3 failed |
| `VIDEO_INDEXING_FAILED` | 500 | TwelveLabs indexing failed |
| `ANALYSIS_FAILED` | 500 | General analysis error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

### Retry Logic
```python
# backend/utils/retry.py
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def call_external_api_with_retry(api_call, *args, **kwargs):
    """
    Retry wrapper for external API calls
    """
    try:
        return await api_call(*args, **kwargs)
    except Exception as e:
        logger.warning(f"API call failed, retrying: {e}")
        raise
```

---

## Rate Limiting & Quotas

### External API Limits

#### TwelveLabs
- **Videos per day:** 100
- **API calls per minute:** 60
- **Concurrent indexing:** 5

**Mitigation:**
```python
# backend/utils/rate_limiter.py
from redis import Redis
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def check_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if rate limit is exceeded
        
        Args:
            key: Unique identifier (e.g., "twelvelabs:videos")
            limit: Max requests allowed
            window: Time window in seconds
        """
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        
        return current <= limit
```

#### ElevenLabs
- **Requests per day:** 1000
- **Audio file size:** 10MB max

#### OpenAI
- **Tokens per minute:** 10,000
- **Requests per minute:** 500

### Internal API Rate Limiting
```python
# backend/api/middleware.py
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting to all endpoints
    """
    # 100 requests per minute per IP
    if not limiter.check_limit("100/minute"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    response = await call_next(request)
    return response
```

---

## Testing & Validation

### 1. Integration Tests

```python
# tests/integration/test_twelvelabs.py
import pytest
from integrations.twelvelabs_client import TwelveLabsClient

@pytest.fixture
def twelvelabs_client():
    return TwelveLabsClient(api_key="test_key")

def test_upload_video(twelvelabs_client):
    """Test video upload and indexing"""
    result = twelvelabs_client.upload_video(
        video_url="https://example.com/test_video.mp4",
        video_title="Test Video"
    )
    
    assert "video_id" in result
    assert result["status"] == "ready"

def test_analyze_creative_elements(twelvelabs_client):
    """Test creative analysis generation"""
    analysis = twelvelabs_client.analyze_creative_elements(
        video_id="test_video_id"
    )
    
    assert "analysis" in analysis
    assert "visual_style" in analysis["analysis"]
```

### 2. Mock Responses for Development

```python
# tests/mocks/twelvelabs_mock.py
class MockTwelveLabsClient:
    """Mock client for testing without API calls"""
    
    def upload_video(self, video_url: str, video_title: str = None):
        return {
            "video_id": "mock_video_123",
            "status": "ready",
            "duration": 60.0
        }
    
    def analyze_creative_elements(self, video_id: str):
        return {
            "video_id": video_id,
            "analysis": {
                "visual_style": "Modern, minimalist",
                "pacing": "Medium",
                "tone": "Professional"
            }
        }
```

### 3. API Health Checks

```python
# backend/api/routes/health.py
from fastapi import APIRouter, HTTPException
from integrations.twelvelabs_client import TwelveLabsClient
from core.config import settings

router = APIRouter()

@router.get("/health/external-apis")
async def check_external_apis():
    """
    Check connectivity to all external APIs
    """
    status = {
        "twelvelabs": "unknown",
        "elevenlabs": "unknown",
        "openai": "unknown"
    }
    
    # Check TwelveLabs
    try:
        client = TwelveLabsClient(api_key=settings.TWELVELABS_API_KEY)
        client.client.indexes.list()
        status["twelvelabs"] = "healthy"
    except Exception as e:
        status["twelvelabs"] = f"unhealthy: {str(e)}"
    
    # Similar checks for other APIs...
    
    all_healthy = all(s == "healthy" for s in status.values())
    
    if not all_healthy:
        raise HTTPException(status_code=503, detail=status)
    
    return status
```

---

## Appendix

### Sample cURL Commands

#### Create Experiment
```bash
curl -X POST http://localhost:8000/api/experiments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Q4 Campaign Test" \
  -F "video_file=@/path/to/video.mp4" \
  -F "results_csv=@/path/to/results.csv" \
  -F "comments_csv=@/path/to/comments.csv"
```

#### Trigger Analysis
```bash
curl -X POST http://localhost:8000/api/experiments/abc-123/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Recommendations
```bash
curl -X GET "http://localhost:8000/api/experiments/abc-123/recommendations?segment=age_18_24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Environment Setup Checklist
- [ ] TwelveLabs API key obtained
- [ ] ElevenLabs API key obtained
- [ ] OpenAI API key obtained
- [ ] AWS S3 bucket created
- [ ] PostgreSQL database provisioned
- [ ] Redis instance running
- [ ] Environment variables configured
- [ ] API health checks passing
