# Quick Start Guide
## Get the Platform Running in 5 Minutes

---

## 🎯 Choose Your Path

### Path A: With TwelveLabs API Key (Full Functionality)
### Path B: Without API Key (Mock Mode for Demo)

---

## Path A: Full Functionality

### Step 1: Get API Keys

1. **TwelveLabs**: https://twelvelabs.io (sign up for free trial)
2. **ElevenLabs**: https://elevenlabs.io (optional - can skip for now)
3. **OpenAI**: https://openai.com (GPT-4 access)
4. **AWS**: For S3 storage (or use local filesystem for testing)

### Step 2: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your keys:
```bash
TWELVELABS_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
ELEVENLABS_API_KEY=your_actual_key_here  # Optional

# For local testing without AWS
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_S3_BUCKET=local-bucket

# Use mock APIs (set to false for real APIs)
USE_MOCK_APIS=false
```

### Step 3: Test TwelveLabs Connection

```bash
cd backend
python test_twelvelabs.py
```

This will verify your API key works.

### Step 4: Start Services

```bash
# Start backend with Docker
docker-compose up -d

# Or manually:
# Terminal 1: Start FastAPI
uvicorn main:app --reload

# Terminal 2: Start Celery worker
celery -A workers.celery_app worker --loglevel=info
```

### Step 5: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

---

## Path B: Mock Mode (No API Keys Needed)

### Step 1: Configure for Mock Mode

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```bash
# Dummy keys (won't be used)
TWELVELABS_API_KEY=mock_key
OPENAI_API_KEY=mock_key
ELEVENLABS_API_KEY=mock_key

# IMPORTANT: Enable mock mode
USE_MOCK_APIS=true

# Local database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/creative_analysis
REDIS_URL=redis://localhost:6379/0
```

### Step 2: Start Services

```bash
cd backend
docker-compose up -d
```

### Step 3: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

### Step 4: Test with Mock Data

The system will now use **simulated TwelveLabs responses**:
- Video upload will succeed instantly
- Analysis will return realistic mock data
- Recommendations will be generated based on mock insights

**Perfect for:**
- Demos without API costs
- Development without API keys
- Testing the UI/UX flow

---

## 🧪 Verify It's Working

### Test 1: Health Check

```bash
curl http://localhost:8000/api/health
```

Should return: `{"status": "healthy"}`

### Test 2: API Docs

Visit: http://localhost:8000/docs

You should see the Swagger UI with all endpoints.

### Test 3: Create Experiment

1. Go to http://localhost:3000
2. Click "New Experiment"
3. Fill in details and upload files
4. Click "Create Experiment"
5. Click "Start Analysis"

**In Mock Mode:** Analysis completes in ~10 seconds  
**In Real Mode:** Analysis takes 3-5 minutes

---

## 📊 Sample Data

Download from: https://github.com/swayable/adweeknyc2025-hackathon

You'll need:
- A video file (`.mp4`)
- Quantitative results CSV (`*_Results.csv`)
- Qualitative comments CSV (`*_Comments.csv`)

---

## 🐛 Troubleshooting

### "TwelveLabs API key invalid"
- Check your `.env` file
- Verify the key at https://twelvelabs.io/dashboard
- Make sure you have credits/quota remaining

### "Database connection failed"
- Ensure PostgreSQL is running: `docker ps`
- Check `DATABASE_URL` in `.env`
- Try: `docker-compose restart postgres`

### "Celery worker not processing"
- Check Redis is running: `redis-cli ping`
- View worker logs: `docker logs creative_analysis_worker`
- Restart worker: `docker-compose restart celery_worker`

### "Frontend can't connect to backend"
- Verify backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`
- Try: `curl http://localhost:8000/api/health`

---

## 🔄 Switching Between Real and Mock Mode

### Enable Mock Mode:
```bash
# In backend/.env
USE_MOCK_APIS=true
```

### Disable Mock Mode (use real APIs):
```bash
# In backend/.env
USE_MOCK_APIS=false
```

Restart services after changing:
```bash
docker-compose restart
```

---

## 📝 Next Steps

1. **Create your first experiment** at http://localhost:3000
2. **Review the recommendations** generated
3. **Export a PDF report**
4. **Read the full documentation** in `README.md`

---

## 💡 Pro Tips

- **Start with Mock Mode** to understand the flow
- **Switch to Real Mode** when you have API keys
- **Use the test script** (`test_twelvelabs.py`) to verify API connectivity
- **Check logs** if something fails: `docker-compose logs -f`

---

**Need help?** Check `README.md` or `DEMO_GUIDE.md`
