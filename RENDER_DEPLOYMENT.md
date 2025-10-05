# Deploy to Render (FREE) - Complete Guide

Deploy your entire platform for **$0/month** using Render's free tier.

---

## 🎯 What You'll Deploy

- ✅ **Frontend** → Vercel (free)
- ✅ **Backend API** → Render (free)
- ✅ **PostgreSQL** → Render (free)
- ✅ **Redis** → Render (free)
- ✅ **Celery Worker** → Render (free)

**Total Cost: $0/month** 🎉

---

## 📋 Prerequisites

1. **GitHub Account** - Your code must be on GitHub
2. **Render Account** - Sign up at https://render.com
3. **Vercel Account** - Sign up at https://vercel.com

---

## Step 1: Push Code to GitHub

```powershell
cd c:\Users\volto\myco

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/creative-analysis-platform.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy PostgreSQL Database

### A. Create Database
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `creative-analysis-db`
   - **Database**: `creative_analysis`
   - **User**: `postgres` (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: **Free**
4. Click **"Create Database"**

### B. Get Database URL
1. Wait 2-3 minutes for database to be ready
2. Copy the **"Internal Database URL"** (starts with `postgresql://`)
3. Save it - you'll need it later

---

## Step 3: Deploy Redis

### A. Create Redis Instance
1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `creative-analysis-redis`
   - **Region**: Same as database
   - **Plan**: **Free**
   - **Maxmemory Policy**: `noeviction`
3. Click **"Create Redis"**

### B. Get Redis URL
1. Wait 1-2 minutes for Redis to be ready
2. Copy the **"Internal Redis URL"** (starts with `redis://`)
3. Save it - you'll need it later

---

## Step 4: Deploy Backend API

### A. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `creative-analysis-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

### B. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```bash
# Database (use the Internal Database URL from Step 2)
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname

# Redis (use the Internal Redis URL from Step 3)
REDIS_URL=redis://host:port
CELERY_BROKER_URL=redis://host:port/1
CELERY_RESULT_BACKEND=redis://host:port/2

# API Keys (your actual keys)
TWELVELABS_API_KEY=tlk_your_actual_key_here
OPENAI_API_KEY=sk-your_actual_key_here
ELEVENLABS_API_KEY=your_actual_key_here

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Security (generate a strong random key)
JWT_SECRET_KEY=your_super_secret_random_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (you'll update this after deploying frontend)
CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Application
ENVIRONMENT=production
DEBUG=False
API_V1_PREFIX=/api
PROJECT_NAME=Creative Pretest Analysis Platform

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# File Upload
MAX_UPLOAD_SIZE_MB=500
ALLOWED_VIDEO_EXTENSIONS=[".mp4",".mov",".avi",".webm"]
ALLOWED_CSV_EXTENSIONS=[".csv"]

# TwelveLabs
TWELVELABS_INDEX_NAME=creative_pretest_index
TWELVELABS_MODEL=pegasus1.2

# Celery
CELERY_TASK_ALWAYS_EAGER=False
CELERY_TASK_EAGER_PROPAGATES=True

# Mock APIs
USE_MOCK_APIS=false
```

### C. Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. Once deployed, you'll get a URL like: `https://creative-analysis-backend.onrender.com`

### D. Run Database Migrations

After deployment completes:
1. Go to your web service dashboard
2. Click **"Shell"** tab
3. Run:
   ```bash
   alembic upgrade head
   ```

Or create a one-time job:
1. Click **"New +"** → **"Background Worker"**
2. Use same settings as web service
3. Start Command: `alembic upgrade head`
4. Run once and delete

---

## Step 5: Deploy Celery Worker

### A. Create Background Worker
1. Click **"New +"** → **"Background Worker"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `creative-analysis-worker`
   - **Region**: Same as others
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A workers.celery_app worker --loglevel=info --concurrency=2`
   - **Plan**: **Free**

### B. Add Same Environment Variables
Copy all environment variables from Step 4B

### C. Deploy
Click **"Create Background Worker"**

---

## Step 6: Deploy Frontend to Vercel

### A. Sign Up / Log In
1. Go to https://vercel.com
2. Sign in with GitHub

### B. Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your `creative-analysis-platform` repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### C. Add Environment Variable
```
Name: VITE_API_URL
Value: https://creative-analysis-backend.onrender.com
```
(Use your actual Render backend URL)

### D. Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. You'll get a URL like: `https://creative-analysis-platform.vercel.app`

---

## Step 7: Update CORS Settings

### A. Update Backend Environment Variable
1. Go to Render dashboard
2. Click on your backend web service
3. Go to **"Environment"** tab
4. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=["https://creative-analysis-platform.vercel.app"]
   ```
   (Use your actual Vercel URL)
5. Click **"Save Changes"**
6. Service will auto-redeploy

---

## Step 8: Test Your Deployment

### A. Test Backend
1. Visit: `https://your-backend.onrender.com/docs`
2. Should see FastAPI documentation
3. Test `/api/health` endpoint - should return `{"status":"healthy"}`

### B. Test Frontend
1. Visit: `https://your-frontend.vercel.app`
2. Should see Creative Insights dashboard
3. Should NOT see "Failed to load experiments"

### C. Test Full Flow
1. Click **"New Experiment"**
2. Fill in details
3. Upload files or use video ID: `68e20c15f2e53b115e1aef18`
4. Create experiment
5. Start analysis
6. Wait for results (may take 5-10 minutes on free tier)

---

## 🎉 You're Live!

Your platform is now deployed for **FREE**:

- **Frontend**: https://your-project.vercel.app
- **Backend**: https://your-backend.onrender.com
- **API Docs**: https://your-backend.onrender.com/docs
- **Database**: PostgreSQL on Render
- **Cache**: Redis on Render
- **Workers**: Celery on Render

**Total Cost: $0/month** 🎊

---

## ⚠️ Important Notes About Free Tier

### Cold Starts
- Services spin down after **15 minutes** of inactivity
- First request after inactivity takes **15-30 seconds** to wake up
- Subsequent requests are fast

### Workarounds:
1. **Use a ping service**: https://uptimerobot.com (free)
   - Ping your backend every 14 minutes to keep it awake
2. **Upgrade to paid**: $7/month removes cold starts

### Limitations:
- **750 hours/month** per service (enough for 1 service 24/7)
- **100 GB bandwidth/month**
- **1 GB RAM** per service
- **0.1 CPU** per service

---

## 🔧 Troubleshooting

### Backend won't start
**Check logs:**
1. Go to Render dashboard
2. Click on your web service
3. Click **"Logs"** tab
4. Look for errors

**Common issues:**
- Missing environment variables
- Database connection failed
- Dependencies not installed

**Solution:**
- Verify all environment variables are set
- Check DATABASE_URL format: `postgresql+asyncpg://...`
- Redeploy service

### Frontend can't connect to backend
**Check:**
1. `VITE_API_URL` in Vercel is correct
2. CORS settings in backend include Vercel URL
3. Backend is running (visit `/docs`)

**Solution:**
- Update `VITE_API_URL` in Vercel
- Update `CORS_ORIGINS` in Render
- Redeploy both services

### Database connection errors
**Check:**
1. DATABASE_URL is correct
2. Database is running
3. Using **Internal Database URL** (not External)

**Solution:**
- Copy Internal Database URL from Render
- Update DATABASE_URL in backend
- Ensure format is `postgresql+asyncpg://...`

### Celery worker not processing tasks
**Check:**
1. Worker service is running
2. Redis URL is correct
3. Worker logs for errors

**Solution:**
- Restart worker service
- Verify REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
- Check worker logs in Render

### Video analysis takes too long
**This is normal on free tier:**
- Free tier has limited CPU
- Analysis may take 10-15 minutes
- Consider upgrading to paid tier for faster processing

---

## 💰 Upgrade Options

If you need better performance:

### Render Paid Plans

**Starter Plan ($7/month per service):**
- ✅ No cold starts
- ✅ 512 MB RAM
- ✅ 0.5 CPU
- ✅ Better for production

**Standard Plan ($25/month per service):**
- ✅ 2 GB RAM
- ✅ 1 CPU
- ✅ Best for production

### Cost Breakdown

**Minimal Production Setup:**
- Backend: $7/month
- Worker: $7/month
- Database: Free (or $7/month for more storage)
- Redis: Free (or $7/month for more memory)
- Frontend: Free (Vercel)
- **Total: ~$14-28/month**

---

## 📊 Monitoring

### Render Dashboard
- View logs in real-time
- Monitor resource usage
- Check deployment history
- View metrics

### Vercel Dashboard
- View deployment logs
- Monitor performance
- Check analytics
- View error logs

### Set Up Alerts
1. Go to Render dashboard
2. Click on service
3. Go to **"Settings"** → **"Notifications"**
4. Add email for deployment notifications

---

## 🔄 Continuous Deployment

Both Render and Vercel auto-deploy when you push to GitHub:

```powershell
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Render and Vercel will automatically deploy!
```

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Issues**: Create an issue in your repo

---

## 📝 Quick Reference

### Render URLs
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

### Your Services
- Backend: `https://creative-analysis-backend.onrender.com`
- Frontend: `https://creative-analysis-platform.vercel.app`
- API Docs: `https://creative-analysis-backend.onrender.com/docs`

### Important Commands
```bash
# View logs
render logs <service-name>

# SSH into service
render shell <service-name>

# Run migrations
alembic upgrade head

# Restart service
# (Use Render dashboard - Manual Deploy → Clear build cache & deploy)
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL created on Render
- [ ] Redis created on Render
- [ ] Backend deployed to Render
- [ ] Celery worker deployed to Render
- [ ] Database migrations run
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS updated with Vercel URL
- [ ] Health check passes
- [ ] Test experiment created
- [ ] Video analysis works
- [ ] Recommendations generated

---

**Congratulations! Your platform is live for FREE!** 🎉🚀

Start analyzing videos and generating insights!
