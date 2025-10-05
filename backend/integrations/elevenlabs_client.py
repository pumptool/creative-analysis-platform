"""
ElevenLabs API client for audio analysis
"""
import requests
import logging
import subprocess
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Client for ElevenLabs audio analysis API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
        """
        Extract audio track from video file using ffmpeg
        
        Args:
            video_path: Path to video file
            output_path: Path for output audio file
            
        Returns:
            Path to extracted audio file
        """
        try:
            command = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "libmp3lame",
                "-q:a", "2",  # High quality
                "-y",  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"Audio extracted to {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e.stderr}")
            raise Exception(f"Failed to extract audio: {e.stderr}")
        except FileNotFoundError:
            logger.error("ffmpeg not found. Please install ffmpeg.")
            raise Exception("ffmpeg is required but not installed")
    
    def analyze_voice_emotion(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Analyze emotional characteristics of voice in audio
        
        Note: This is a placeholder implementation.
        Actual ElevenLabs API endpoints may differ.
        
        Returns:
        - Dominant emotion
        - Emotion distribution
        - Voice characteristics (pitch, pace, energy)
        """
        try:
            # Placeholder: ElevenLabs may not have direct emotion analysis
            # This would need to be adapted based on actual API capabilities
            
            # For now, return a mock structure
            logger.warning("Using placeholder emotion analysis")
            
            return {
                "dominant_emotion": "confident",
                "emotion_scores": {
                    "confident": 0.65,
                    "friendly": 0.25,
                    "neutral": 0.10
                },
                "voice_characteristics": {
                    "pitch": "medium",
                    "pace": "moderate",
                    "energy": "high",
                    "clarity": 0.92
                }
            }
            
        except Exception as e:
            logger.error(f"Voice emotion analysis failed: {e}")
            raise
    
    def analyze_audio_quality(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Assess technical quality of audio
        
        Returns:
        - Audio clarity score
        - Background noise level
        - Volume consistency
        """
        try:
            # Placeholder implementation
            logger.warning("Using placeholder audio quality analysis")
            
            return {
                "clarity_score": 0.88,
                "noise_level": 0.12,
                "volume_consistency": 0.85,
                "overall_quality": "good"
            }
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            raise
    
    def get_audio_insights(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive audio insights
        
        Combines emotion and quality analysis
        """
        try:
            emotion = self.analyze_voice_emotion(audio_file_path)
            quality = self.analyze_audio_quality(audio_file_path)
            
            return {
                "emotion_analysis": emotion,
                "quality_analysis": quality,
                "recommendations": self._generate_audio_recommendations(emotion, quality)
            }
            
        except Exception as e:
            logger.error(f"Audio insights generation failed: {e}")
            raise
    
    def _generate_audio_recommendations(
        self,
        emotion: Dict[str, Any],
        quality: Dict[str, Any]
    ) -> list[str]:
        """Generate audio-specific recommendations"""
        recommendations = []
        
        # Check emotion alignment
        if emotion["dominant_emotion"] in ["sad", "angry", "fearful"]:
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
        
        if quality["volume_consistency"] < 0.7:
            recommendations.append(
                "Volume levels are inconsistent - apply audio normalization"
            )
        
        return recommendations
