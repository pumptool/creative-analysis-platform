# Testing Instructions

## Prerequisites Check

Before testing, ensure you have:
- [ ] Python 3.11+ installed
- [ ] TwelveLabs API key (or use mock mode)
- [ ] Dependencies installed

---

## Step 1: Install Python (if needed)

### Option A: Download from python.org
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later
3. **Important**: Check "Add Python to PATH" during installation

### Option B: Use Microsoft Store
1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click Install

### Verify Installation
```powershell
python --version
# Should show: Python 3.11.x or later
```

---

## Step 2: Set Up Environment

### Navigate to backend directory
```powershell
cd c:\Users\volto\myco\backend
```

### Create virtual environment (recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies
```powershell
pip install -r requirements.txt
```

---

## Step 3: Configure API Key

### Option A: Use Real TwelveLabs API

1. **Get API Key**:
   - Go to https://playground.twelvelabs.io/
   - Sign up (free account)
   - Get API key from https://playground.twelvelabs.io/dashboard/api-key

2. **Edit `.env` file**:
   ```powershell
   notepad .env
   ```
   
   Change this line:
   ```
   TWELVELABS_API_KEY=your_twelvelabs_api_key_here
   ```
   
   To:
   ```
   TWELVELABS_API_KEY=tlk_your_actual_key_here
   ```
   
   Add this line:
   ```
   USE_MOCK_APIS=false
   ```

### Option B: Use Mock Mode (No API Key Needed)

Edit `.env` file:
```powershell
notepad .env
```

Add this line:
```
USE_MOCK_APIS=true
```

---

## Step 4: Run Tests

### Test 1: Connection Test Only

```powershell
python test_twelvelabs.py
```

When prompted for video URL, **press Enter to skip** (tests connection only).

**Expected Output:**
```
============================================================
TwelveLabs Integration Test
============================================================
Testing TwelveLabs API connection...
✅ TwelveLabs client initialized
✅ Index ID: abc123...

Video Upload Test (Optional)
Enter a video URL to test (or press Enter to skip): [Press Enter]

⏭️  Skipping video upload test
============================================================
✅ All tests completed!
============================================================
```

### Test 2: Full Test with Video

```powershell
python test_twelvelabs.py
```

When prompted, enter this test video URL:
```
https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4
```

**Expected Output:**
```
Testing video upload: https://storage...
Uploading video to TwelveLabs...
(This may take a few minutes depending on video length)
Created task: id=xyz789
  Indexing status=processing
  Indexing status=ready

✅ Video uploaded successfully!
   Video ID: video_abc123
   Status: ready
   Duration: 734.0 seconds

Analyzing video creative elements...
(Using gist, summarize, and analyze APIs)

✅ Analysis complete!

   Title: Tears of Steel
   Topics: ['science fiction', 'action', 'drama']
   Summary: A group of warriors and scientists...

Testing video segmentation for video ID: video_abc123
✅ Found 5 chapters/scenes

First chapter:
   Title: Opening Scene
   Start: 0.0s
   End: 120.5s
   Summary: The video opens with a dramatic...

Testing key moments/highlights...
✅ Found 3 key moments

First highlight: Intense action sequence begins
```

---

## Step 5: Test Full Platform

### Start Backend Services

#### Option A: Using Docker (Recommended)
```powershell
cd c:\Users\volto\myco\backend
docker-compose up -d
```

#### Option B: Manual Start
```powershell
# Terminal 1: Start FastAPI
cd c:\Users\volto\myco\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload

# Terminal 2: Start Celery Worker
cd c:\Users\volto\myco\backend
.\venv\Scripts\Activate.ps1
celery -A workers.celery_app worker --loglevel=info
```

### Start Frontend

```powershell
# Terminal 3: Start React
cd c:\Users\volto\myco\frontend
npm install
npm run dev
```

### Access Application

Open browser to: **http://localhost:3000**

---

## Step 6: Create Test Experiment

1. Click **"New Experiment"**
2. Fill in:
   - **Title**: "Test Campaign"
   - **Video URL**: `https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4`
   - **Upload sample CSV files** (create dummy ones if needed)
3. Click **"Create Experiment"**
4. Click **"Start Analysis"**
5. Wait 3-5 minutes
6. View recommendations!

---

## Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Users\volto\AppData\Local\Programs\Python\Python311\python.exe`

### "ModuleNotFoundError: No module named 'twelvelabs'"
```powershell
pip install twelvelabs
```

### "ModuleNotFoundError: No module named 'dotenv'"
```powershell
pip install python-dotenv
```

### "Invalid API key"
- Check your key at https://playground.twelvelabs.io/dashboard/api-key
- Make sure it starts with `tlk_`
- Verify you copied it correctly (no extra spaces)

### "Connection refused"
- Make sure PostgreSQL is running: `docker ps`
- Make sure Redis is running: `docker ps`
- Check `DATABASE_URL` in `.env`

### "Indexing timeout"
- Video might be too long (try shorter video)
- Check internet connection
- Verify video URL is accessible

---

## Quick Test Commands

### Just test connection (no video upload):
```powershell
cd c:\Users\volto\myco\backend
python test_twelvelabs.py
# Press Enter when prompted for video URL
```

### Test with sample video:
```powershell
cd c:\Users\volto\myco\backend
python test_twelvelabs.py
# Enter: https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4
```

### Check if services are running:
```powershell
# Check backend
curl http://localhost:8000/api/health

# Check frontend
curl http://localhost:3000
```

---

## Mock Mode Testing

If you don't have a TwelveLabs API key yet:

1. Edit `.env`:
   ```
   USE_MOCK_APIS=true
   ```

2. Run test:
   ```powershell
   python test_twelvelabs.py
   ```

3. You'll see:
   ```
   Using MOCK TwelveLabs client (no real API calls)
   ```

4. Everything will work, but with simulated data

---

## What to Expect

### With Real API:
- ✅ Actual video analysis from TwelveLabs
- ✅ Real titles, topics, summaries
- ✅ Accurate chapter breakdown
- ✅ Genuine highlights
- ⏱️ Takes 3-5 minutes per video
- 💰 Costs ~$0.50 per video

### With Mock Mode:
- ✅ Simulated responses
- ✅ Instant results (no waiting)
- ✅ Good for UI/UX testing
- ✅ Free (no API costs)
- ⚠️ Not real analysis

---

## Next Steps After Testing

1. ✅ **Test passes** → You're ready to use the platform!
2. 📊 **Create experiments** → Upload your own videos
3. 📈 **View insights** → Get AI-powered recommendations
4. 📄 **Export reports** → Share with stakeholders
5. 🚀 **Deploy** → Follow `DEPLOYMENT.md` for production

---

## Need Help?

- **Documentation**: See `README.md`, `QUICK_START.md`
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **TwelveLabs Docs**: https://docs.twelvelabs.io/
- **Integration Guide**: See `TWELVELABS_INTEGRATION.md`

---

**Ready to test? Start with Step 1! 🚀**
