# Quick Deploy to Vercel - Step by Step

Follow these exact steps to deploy your platform.

---

## Step 1: Push to GitHub

```powershell
# Navigate to your project
cd c:\Users\volto\myco

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Creative Analysis Platform ready for deployment"

# Create a new repository on GitHub:
# 1. Go to https://github.com/new
# 2. Name it: creative-analysis-platform
# 3. Make it Private (recommended)
# 4. Don't initialize with README (we already have one)
# 5. Click "Create repository"

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/creative-analysis-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Frontend to Vercel

### A. Sign Up / Log In
1. Go to https://vercel.com
2. Click "Sign Up" or "Log In"
3. Sign in with GitHub

### B. Import Project
1. Click "Add New..." → "Project"
2. Find your `creative-analysis-platform` repository
3. Click "Import"

### C. Configure Build Settings
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### D. Add Environment Variable
Click "Environment Variables" and add:
```
Name: VITE_API_URL
Value: https://your-backend-url.com
```
(You'll update this after deploying the backend)

### E. Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Your frontend will be live at: `https://your-project.vercel.app`

---

## Step 3: Deploy Backend to Railway

### A. Sign Up
1. Go to https://railway.app
2. Sign up with GitHub
3. Verify your email

### B. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `creative-analysis-platform` repository
4. Railway will detect it's a Python project

### C. Configure Root Directory
1. In project settings, set:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### D. Add PostgreSQL
1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically set `DATABASE_URL`

### E. Add Redis
1. Click "New" → "Database" → "Add Redis"
2. Railway will automatically set `REDIS_URL`

### F. Add Environment Variables
Click on your backend service → "Variables" → Add these:

```bash
# API Keys
TWELVELABS_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
ELEVENLABS_API_KEY=your_actual_key_here

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Security
JWT_SECRET_KEY=generate_a_strong_random_key_here
JWT_ALGORITHM=HS256

# CORS (update with your Vercel URL)
CORS_ORIGINS=["https://your-project.vercel.app"]

# Application
ENVIRONMENT=production
DEBUG=False
API_V1_PREFIX=/api

# Redis (Railway sets these automatically, but verify)
CELERY_BROKER_URL=${{Redis.REDIS_URL}}/1
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}/2

# Database (Railway sets this automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### G. Deploy
1. Railway will automatically deploy
2. Wait 5-10 minutes for first deployment
3. Get your backend URL from Railway dashboard

### H. Run Database Migrations
In Railway dashboard:
1. Click on your backend service
2. Go to "Settings" → "Deploy"
3. Add a deploy command: `alembic upgrade head`

Or use Railway CLI:
```bash
railway run alembic upgrade head
```

---

## Step 4: Update Frontend with Backend URL

### A. Update Vercel Environment Variable
1. Go to your Vercel project
2. Settings → Environment Variables
3. Edit `VITE_API_URL`
4. Change to your Railway backend URL: `https://your-backend.railway.app`
5. Click "Save"

### B. Redeploy Frontend
1. Go to "Deployments" tab
2. Click "..." on latest deployment
3. Click "Redeploy"

---

## Step 5: Add Celery Worker (Optional but Recommended)

### In Railway:
1. Click "New" → "Empty Service"
2. Name it "celery-worker"
3. Connect same GitHub repo
4. Set Root Directory: `backend`
5. Set Start Command: `celery -A workers.celery_app worker --loglevel=info`
6. Add same environment variables as backend
7. Deploy

---

## Step 6: Test Your Deployment

### A. Test Frontend
1. Visit your Vercel URL: `https://your-project.vercel.app`
2. Should see the Creative Insights dashboard
3. Click "New Experiment"

### B. Test Backend
1. Visit: `https://your-backend.railway.app/docs`
2. Should see FastAPI documentation
3. Test `/api/health` endpoint

### C. Test Full Flow
1. Create a new experiment
2. Upload video (or use video ID)
3. Upload CSV files
4. Start analysis
5. Wait for results
6. View recommendations

---

## 🎉 You're Live!

Your platform is now deployed:
- **Frontend**: https://your-project.vercel.app
- **Backend**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs

---

## 🔧 Troubleshooting

### Frontend shows "Failed to load experiments"
- Check `VITE_API_URL` is correct
- Verify backend is running
- Check CORS settings in backend

### Backend deployment fails
- Check all environment variables are set
- Verify `requirements.txt` is complete
- Check Railway logs for errors

### Database connection errors
- Verify `DATABASE_URL` is set by Railway
- Check PostgreSQL service is running
- Try redeploying

### Celery worker not processing
- Check Redis is running
- Verify worker environment variables
- Check worker logs in Railway

---

## 📊 Monitoring

### Vercel
- Dashboard → Your Project → Analytics
- View deployment logs
- Monitor performance

### Railway
- Dashboard → Your Project → Metrics
- View application logs
- Monitor resource usage

---

## 💰 Costs

### Free Tier (Development)
- **Vercel**: Free (Hobby plan)
- **Railway**: $5/month trial credit
- **Total**: Free for first month

### Production
- **Vercel Pro**: $20/month
- **Railway**: ~$20-50/month (depending on usage)
- **Total**: ~$40-70/month

---

## 🆘 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: Create an issue in your repo

---

**Deployment completed!** 🚀

Share your live URL and start analyzing videos!
