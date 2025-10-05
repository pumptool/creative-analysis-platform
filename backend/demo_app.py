"""
Simplified demo app - Works without database
For quick testing of TwelveLabs integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

load_dotenv()

app = FastAPI(title="Creative Analysis Demo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TwelveLabs client
TL_API_KEY = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
tl_client = TwelveLabs(api_key=TL_API_KEY) if TL_API_KEY else None

# In-memory storage (for demo)
videos_db = {}


class VideoAnalyzeRequest(BaseModel):
    video_id: str


class VideoAnalysisResponse(BaseModel):
    video_id: str
    title: str
    topics: List[str]
    hashtags: List[str]
    summary: str
    chapters: List[dict]
    highlights: List[dict]
    detailed_analysis: str


@app.get("/")
def root():
    return {
        "message": "Creative Analysis Platform - Demo Mode",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "twelvelabs_connected": tl_client is not None
    }


@app.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalyzeRequest):
    """
    Analyze a video using TwelveLabs API
    
    Provide a video_id that has already been indexed in TwelveLabs
    """
    if not tl_client:
        raise HTTPException(status_code=500, detail="TwelveLabs API key not configured")
    
    video_id = request.video_id
    
    try:
        print(f"Analyzing video: {video_id}")
        
        # 1. Get Gist
        print("  Getting gist...")
        gist = tl_client.gist(video_id=video_id, types=["title", "topic", "hashtag"])
        
        # 2. Get Summary
        print("  Getting summary...")
        summary_result = tl_client.summarize(video_id=video_id, type="summary")
        
        # 3. Get Chapters
        print("  Getting chapters...")
        chapters_result = tl_client.summarize(video_id=video_id, type="chapter")
        
        # 4. Get Highlights
        print("  Getting highlights...")
        highlights_result = tl_client.summarize(video_id=video_id, type="highlight")
        
        # 5. Get Detailed Analysis
        print("  Getting detailed analysis...")
        analysis_prompt = """Analyze this video for creative effectiveness:
        - Visual style and composition
        - Pacing and editing
        - Audio and messaging
        - Key moments
        - Recommendations for improvement"""
        
        analysis_text = ""
        text_stream = tl_client.analyze_stream(
            video_id=video_id,
            prompt=analysis_prompt
        )
        
        for text in text_stream:
            if text.event_type == "text_generation":
                analysis_text += text.text
        
        # Build response
        response = VideoAnalysisResponse(
            video_id=video_id,
            title=gist.title,
            topics=gist.topics,
            hashtags=gist.hashtags,
            summary=summary_result.summary,
            chapters=[
                {
                    "chapter_number": ch.chapter_number,
                    "start_sec": ch.start_sec,
                    "end_sec": ch.end_sec,
                    "title": ch.chapter_title,
                    "summary": ch.chapter_summary
                }
                for ch in chapters_result.chapters
            ],
            highlights=[
                {
                    "highlight": h.highlight,
                    "start_sec": h.start_sec,
                    "end_sec": h.end_sec
                }
                for h in highlights_result.highlights
            ],
            detailed_analysis=analysis_text
        )
        
        # Cache result
        videos_db[video_id] = response
        
        print(f"  Analysis complete!")
        return response
        
    except Exception as e:
        print(f"  Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze/{video_id}", response_model=VideoAnalysisResponse)
async def get_analysis(video_id: str):
    """Get cached analysis for a video"""
    if video_id in videos_db:
        return videos_db[video_id]
    else:
        raise HTTPException(status_code=404, detail="Video not analyzed yet. Use POST /analyze first.")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting Creative Analysis Platform - Demo Mode")
    print("=" * 60)
    print("\nEndpoints:")
    print("  - Health: http://localhost:8000/health")
    print("  - Analyze: POST http://localhost:8000/analyze")
    print("  - API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
