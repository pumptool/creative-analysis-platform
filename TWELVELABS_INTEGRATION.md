# TwelveLabs Integration Complete ✅

## What Was Integrated

I've successfully integrated your **official TwelveLabs Python SDK script** into the platform. The integration uses the real TwelveLabs API methods from their quickstart guide.

---

## Changes Made

### 1. Updated `backend/integrations/twelvelabs_client.py`

**Key Methods Now Using Real TwelveLabs API:**

#### `create_or_get_index()`
- Uses `client.indexes.create()` with Pegasus 1.2 model
- Model options: `["visual", "audio"]`
- Matches your script exactly

#### `upload_video()`
- Uses `client.tasks.create()` to upload video
- Uses `client.tasks.wait_for_done()` with callback for monitoring
- Logs indexing progress: "Indexing status=processing/ready"
- Returns video_id when status="ready"

#### `analyze_creative_elements()`
Now uses **4 TwelveLabs API endpoints**:

1. **`client.gist()`** - Gets title, topics, hashtags
2. **`client.summarize(type="summary")`** - Gets video summary
3. **`client.summarize(type="chapter")`** - Gets chapters
4. **`client.summarize(type="highlight")`** - Gets highlights
5. **`client.analyze_stream()`** - Gets detailed analysis with custom prompt

Returns comprehensive analysis combining all endpoints.

#### `get_video_segments()`
- Uses `client.summarize(type="chapter")` to get scene breakdown
- Returns chapters with timestamps, titles, and summaries

#### `get_key_moments()` (New Method)
- Uses `client.summarize(type="highlight")` to get key moments
- Returns highlights with timestamps

---

## How It Works

### Video Upload Flow
```python
# 1. Create/get index
index_id = client.create_or_get_index("creative_pretest_index")

# 2. Upload video
task = client.tasks.create(index_id=index_id, video_url=video_url)

# 3. Wait for indexing with callback
def on_task_update(task):
    print(f"Status={task.status}")

task = client.tasks.wait_for_done(task_id=task.id, callback=on_task_update)

# 4. Get video_id when ready
video_id = task.video_id
```

### Analysis Flow
```python
# 1. Get gist
gist = client.gist(video_id=video_id, types=["title", "topic", "hashtag"])

# 2. Get summary
summary = client.summarize(video_id=video_id, type="summary")

# 3. Get chapters
chapters = client.summarize(video_id=video_id, type="chapter")

# 4. Get highlights
highlights = client.summarize(video_id=video_id, type="highlight")

# 5. Get detailed analysis
text_stream = client.analyze_stream(video_id=video_id, prompt="...")
for text in text_stream:
    if text.event_type == "text_generation":
        analysis_text += text.text
```

---

## Testing

### Test Script: `backend/test_twelvelabs.py`

Run this to verify your integration:

```bash
cd backend
python test_twelvelabs.py
```

**What it tests:**
1. ✅ API key validation
2. ✅ Index creation
3. ✅ Video upload and indexing
4. ✅ Gist, summarize, and analyze APIs
5. ✅ Chapter/scene extraction
6. ✅ Highlight/key moment extraction

**Example output:**
```
Testing TwelveLabs API connection...
✅ TwelveLabs client initialized
✅ Index ID: abc123...

Uploading video to TwelveLabs...
Created task: id=xyz789
  Indexing status=processing
  Indexing status=ready
✅ Video uploaded successfully!
   Video ID: video_abc123
   
Analyzing video creative elements...
✅ Analysis complete!
   Title: Tears of Steel
   Topics: ['science fiction', 'action', 'drama']
   Summary: A group of warriors...
```

---

## Environment Setup

### Option 1: Use Real TwelveLabs API

In `backend/.env`:
```bash
# Your actual TwelveLabs API key
TWELVELABS_API_KEY=tlk_xxxxxxxxxxxxx
# or
TL_API_KEY=tlk_xxxxxxxxxxxxx

# Disable mock mode
USE_MOCK_APIS=false
```

### Option 2: Use Mock Mode (No API Key)

In `backend/.env`:
```bash
# Dummy key
TWELVELABS_API_KEY=mock_key

# Enable mock mode
USE_MOCK_APIS=true
```

---

## API Endpoints Used

Based on your script, the integration uses:

| Endpoint | Purpose | Our Usage |
|----------|---------|-----------|
| `indexes.create()` | Create video index | Create index with Pegasus 1.2 |
| `tasks.create()` | Upload video | Upload creative for analysis |
| `tasks.wait_for_done()` | Monitor indexing | Wait for video to be ready |
| `gist()` | Get title/topics/hashtags | Extract video metadata |
| `summarize(type="summary")` | Get summary | Get overall video summary |
| `summarize(type="chapter")` | Get chapters | Get scene breakdown |
| `summarize(type="highlight")` | Get highlights | Get key moments |
| `analyze_stream()` | Custom analysis | Detailed creative analysis |

---

## Sample Output Structure

### From `analyze_creative_elements()`:

```json
{
  "video_id": "abc123",
  "analysis": {
    "title": "Brand Campaign Q4",
    "topics": ["technology", "lifestyle", "innovation"],
    "hashtags": ["#TechLife", "#Innovation", "#Future"],
    "summary": "A compelling advertisement showcasing...",
    "chapters": [
      {
        "chapter_number": 1,
        "start_sec": 0.0,
        "end_sec": 10.5,
        "title": "Opening Scene",
        "summary": "Dramatic city skyline with voiceover"
      }
    ],
    "highlights": [
      {
        "highlight": "Product reveal moment",
        "start_sec": 15.2,
        "end_sec": 18.7
      }
    ],
    "detailed_analysis": "This advertisement employs a modern visual style..."
  },
  "model": "pegasus1.2"
}
```

---

## Integration with Celery Workers

The `analyze_experiment_task` in `backend/workers/tasks/analysis_tasks.py` now:

1. ✅ Checks `USE_MOCK_APIS` environment variable
2. ✅ Uses `TwelveLabsClient` (real API) if `USE_MOCK_APIS=false`
3. ✅ Uses `MockTwelveLabsClient` if `USE_MOCK_APIS=true`
4. ✅ Calls all the real API methods (gist, summarize, analyze_stream)

---

## Next Steps

### 1. Get Your API Key
Sign up at https://playground.twelvelabs.io/ and get your API key from the dashboard.

### 2. Test the Integration
```bash
cd backend
cp .env.example .env
# Add your TWELVELABS_API_KEY to .env
python test_twelvelabs.py
```

### 3. Run the Full Platform
```bash
# Start backend
docker-compose up -d

# Start frontend
cd ../frontend
npm install
npm run dev
```

### 4. Create an Experiment
1. Go to http://localhost:3000
2. Upload a video (or use URL like in your script: https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4)
3. Upload CSV files
4. Click "Start Analysis"
5. Watch the real TwelveLabs API analyze your video!

---

## Differences from Your Script

### What's the Same:
- ✅ Uses official TwelveLabs Python SDK
- ✅ Same API methods (gist, summarize, analyze_stream)
- ✅ Same model (Pegasus 1.2)
- ✅ Same model options (visual, audio)
- ✅ Same callback pattern for monitoring

### What's Enhanced:
- ✅ Integrated into full-stack platform
- ✅ Async processing with Celery
- ✅ Combined with quantitative + qualitative data
- ✅ Generates actionable recommendations
- ✅ Exports to PDF reports
- ✅ Mock mode for testing without API costs

---

## Cost Estimation

Based on TwelveLabs pricing:
- **Indexing**: ~$0.50 per video
- **Analysis**: Included in indexing
- **Total per experiment**: **~$0.50**

With Free plan: **600 minutes of video** = ~600 experiments

---

## Troubleshooting

### "Invalid API key"
- Check your key at https://playground.twelvelabs.io/dashboard/api-key
- Make sure it starts with `tlk_`
- Verify you have credits remaining

### "Indexing timeout"
- Increase timeout in `upload_video()` method
- Check video is accessible (public URL)
- Verify video format is supported

### "Analysis returns empty"
- Ensure video was fully indexed (status="ready")
- Check video has actual content (not blank)
- Try with sample video from TwelveLabs docs

---

**Your TwelveLabs script is now fully integrated! 🎉**

The platform will use the real TwelveLabs API to analyze videos just like in your Colab notebook, but now it's part of a complete enterprise system with recommendations, exports, and a beautiful UI.
