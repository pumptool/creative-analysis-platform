# Vercel Deployment Guide

This guide will help you deploy your Creative Analysis Platform to Vercel.

---

## 🎯 Deployment Strategy

Since this is a full-stack application with:
- **Frontend**: React/TypeScript (can deploy to Vercel)
- **Backend**: FastAPI/Python (needs separate hosting)
- **Database**: PostgreSQL (needs separate hosting)
- **Redis**: For Celery workers (needs separate hosting)

**You have two options:**

---

## Option 1: Frontend Only on Vercel (Recommended)

Deploy the frontend to Vercel and host the backend elsewhere.

### Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Vercel Account** - Sign up at https://vercel.com
3. **Backend Hosted** - Deploy backend to:
   - Railway (recommended for Python)
   - Render
   - Heroku
   - AWS/GCP/Azure
   - Your own server

### Step 1: Prepare Frontend for Production

```bash
cd frontend

# Update .env.production with your backend URL
# Edit: frontend/.env.production
VITE_API_URL=https://your-backend-api.com
```

### Step 2: Test Production Build Locally

```bash
npm run build
npm run preview
```

Visit http://localhost:4173 to test the production build.

### Step 3: Push to GitHub

```bash
cd c:\Users\volto\myco

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Creative Analysis Platform"

# Create GitHub repo and push
# Follow GitHub instructions to add remote and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Add Environment Variables**:
   - Key: `VITE_API_URL`
   - Value: `https://your-backend-api.com`

6. **Click "Deploy"**

### Step 5: Configure Custom Domain (Optional)

1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

---

## Option 2: Full Stack on Vercel (Limited)

⚠️ **Note**: Vercel has limitations for Python backends. This is not recommended for production.

### Using Vercel Serverless Functions

Create serverless functions for simple API endpoints:

```bash
# Create api directory in root
mkdir api

# Create a simple Python function
# api/health.py
```

**Limitations**:
- No WebSocket support
- No long-running processes (Celery workers won't work)
- Cold starts
- Limited execution time (10s for Hobby, 60s for Pro)

**Not suitable for**:
- Video processing
- Long-running analysis tasks
- Celery workers
- Database migrations

---

## 🚀 Recommended Full Deployment Architecture

### Frontend: Vercel
- **Service**: Vercel
- **Cost**: Free tier available
- **Setup**: Connect GitHub repo

### Backend: Railway
- **Service**: Railway (https://railway.app)
- **Cost**: $5/month + usage
- **Features**:
  - PostgreSQL included
  - Redis included
  - Easy Python deployment
  - Environment variables
  - Auto-deploy from GitHub

### Alternative Backend Options:

#### 1. Render (https://render.com)
- Free tier available
- PostgreSQL included
- Redis available
- Auto-deploy from GitHub

#### 2. Fly.io (https://fly.io)
- Free tier available
- PostgreSQL and Redis available
- Docker-based deployment

#### 3. AWS/GCP/Azure
- Most flexible
- More complex setup
- Higher cost but more control

---

## 📋 Backend Deployment Checklist

Wherever you deploy your backend, ensure:

### Environment Variables
```bash
# API Keys
TWELVELABS_API_KEY=your_key
OPENAI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket

# Security
JWT_SECRET_KEY=your_secret_key

# CORS
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### Required Services
- ✅ PostgreSQL database
- ✅ Redis instance
- ✅ Python 3.11+ runtime
- ✅ Background worker for Celery

### Deployment Files
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` or `railway.toml` - Process configuration
- ✅ `Dockerfile` (optional) - Container configuration

---

## 🔧 Quick Deploy to Railway (Backend)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd backend
railway init
```

### Step 4: Add Services

```bash
# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis
```

### Step 5: Set Environment Variables

```bash
railway variables set TWELVELABS_API_KEY=your_key
railway variables set OPENAI_API_KEY=your_key
# ... add all other variables
```

### Step 6: Deploy

```bash
railway up
```

### Step 7: Get Backend URL

```bash
railway domain
```

Use this URL in your frontend's `VITE_API_URL`.

---

## 📝 Post-Deployment Steps

### 1. Update Frontend Environment

```bash
# In Vercel dashboard, update environment variable:
VITE_API_URL=https://your-backend-url.railway.app
```

### 2. Run Database Migrations

```bash
# SSH into your backend or use Railway CLI
railway run alembic upgrade head
```

### 3. Test Deployment

- Visit your Vercel frontend URL
- Test creating an experiment
- Verify video analysis works
- Check recommendations generation

### 4. Monitor

- **Vercel**: Check deployment logs
- **Railway**: Check application logs
- **Sentry** (optional): Add error tracking

---

## 🔒 Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable authentication
- [ ] Secure API keys (use environment variables)
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring

---

## 💰 Cost Estimation

### Minimal Setup (Hobby/Development)

| Service | Plan | Cost |
|---------|------|------|
| Vercel (Frontend) | Hobby | Free |
| Railway (Backend + DB + Redis) | Starter | $5/month + usage |
| TwelveLabs API | Free tier | Free (600 min) |
| **Total** | | **~$5-20/month** |

### Production Setup

| Service | Plan | Cost |
|---------|------|------|
| Vercel (Frontend) | Pro | $20/month |
| Railway (Backend) | Pro | $20/month + usage |
| AWS S3 (Storage) | Pay-as-you-go | ~$5/month |
| TwelveLabs API | Pay-as-you-go | ~$0.50/video |
| **Total** | | **~$50-100/month** |

---

## 🆘 Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_URL` is correct
- Verify CORS settings in backend
- Check backend is running

### Database connection errors
- Verify `DATABASE_URL` format
- Check database is accessible
- Ensure SSL mode is correct

### Celery workers not running
- Check Redis connection
- Verify worker process is running
- Check worker logs

### Video upload fails
- Check S3 credentials
- Verify bucket permissions
- Check file size limits

---

## 📚 Additional Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **PostgreSQL on Railway**: https://docs.railway.app/databases/postgresql

---

## ✅ Quick Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] PostgreSQL database created
- [ ] Redis instance created
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] CORS configured
- [ ] API keys added
- [ ] Domain configured (optional)
- [ ] SSL enabled
- [ ] Monitoring set up
- [ ] Backups configured

---

**Need help?** Check the documentation or create an issue on GitHub!
