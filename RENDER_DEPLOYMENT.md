# 🚀 CLARITY - Render Deployment Guide

## Complete Guide to Deploying CLARITY on Render

---

## 🔥 ISSUES FOUND & FIXED

### ❌ Problems That Caused Build Failures:

1. **SQLAlchemy 2.0 Incompatibility**
   - Old: `db.engine.execute('SELECT 1')` (deprecated)
   - Fixed: `conn.execute(text('SELECT 1'))` (SQLAlchemy 2.0 compatible)

2. **Heavy Dependencies**
   - opencv-python, moviepy, spacy, transformers = 2GB+ packages
   - Build timeout on Render (15 min limit)
   - Fixed: Created `requirements-render.txt` with only essential packages

3. **Missing System Dependencies**
   - Tesseract, poppler-utils needed but not installed
   - Fixed: Commented out OCR dependencies (optional)

4. **ChromaDB Issues**
   - Can be problematic on some platforms
   - Fixed: Using tested version 0.4.22

---

## ✅ SOLUTIONS PROVIDED

### 1. **Fixed build.sh** (SQLAlchemy 2.0 compatible)
### 2. **Created requirements-render.txt** (Optimized, faster builds)
### 3. **Created render.yaml** (Complete Render config)
### 4. **Created build-render.sh** (Render-specific build script)

---

## 🚀 DEPLOYMENT STEPS

### Option A: Deploy with render.yaml (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables** (in Render Dashboard)
   ```env
   FLASK_SECRET_KEY=your-secret-key-here
   GOOGLE_API_KEY=your-gemini-key-here
   OPENAI_API_KEY=your-openai-key  # Optional
   ANTHROPIC_API_KEY=your-claude-key  # Optional
   GROQ_API_KEY=your-groq-key  # Optional
   ```

4. **Deploy**
   - Click "Apply"
   - Render will create: Web service, Worker, PostgreSQL, Redis
   - Wait 10-15 minutes for build

---

### Option B: Manual Deployment

#### Step 1: Create PostgreSQL Database
1. Go to Render Dashboard
2. New → PostgreSQL
3. Name: `clarity-db`
4. Plan: Free or Starter
5. Create Database
6. Copy `Internal Database URL`

#### Step 2: Create Redis Instance
1. New → Redis
2. Name: `clarity-redis`
3. Plan: Free or Starter
4. Create Redis
5. Copy `Internal Redis URL`

#### Step 3: Create Web Service
1. New → Web Service
2. Connect your GitHub repo
3. **Configuration:**
   - Name: `clarity-web`
   - Environment: `Python 3`
   - Build Command: `./build-render.sh`
   - Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2`
   - Plan: Free or Starter

4. **Environment Variables:**
   ```env
   PYTHON_VERSION=3.11.6
   FLASK_ENV=production
   FLASK_DEBUG=false
   FLASK_SECRET_KEY=your-secret-key
   DATABASE_URL=[paste Internal Database URL]
   REDIS_URL=[paste Internal Redis URL]
   CELERY_BROKER_URL=[paste Internal Redis URL]
   CELERY_RESULT_BACKEND=[paste Internal Redis URL]
   GOOGLE_API_KEY=your-gemini-key
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-claude-key
   GROQ_API_KEY=your-groq-key
   ```

5. **Create Service**

#### Step 4: Create Background Worker
1. New → Background Worker
2. Same repo as web service
3. **Configuration:**
   - Name: `clarity-worker`
   - Build Command: `./build-render.sh`
   - Start Command: `celery -A celery_worker.celery_app worker --loglevel=info`
   - Same environment variables as web service

---

## 📦 OPTIMIZED FOR RENDER

### Using requirements-render.txt

The optimized requirements file:
- **Removes**: opencv, moviepy, spacy, transformers (2GB+)
- **Keeps**: All core features (LLM, data science, expense tracking)
- **Build time**: ~5-8 minutes (vs 15+ minutes timeout)

**To enable heavy features later:**
1. Uncomment packages in `requirements-render.txt`
2. Increase Render plan (more build time)
3. Redeploy

---

## 🔧 BUILD COMMANDS

### For Render (Recommended)
```bash
./build-render.sh
```

### For Local Development
```bash
./build.sh
```

---

## ⚙️ RENDER CONFIGURATION

### Web Service Settings
- **Instance Type**: Starter ($7/month) or Free
- **Region**: Choose closest to your users
- **Auto-Deploy**: Enable for GitHub pushes
- **Health Check Path**: `/` (landing page)

### Worker Settings
- **Instances**: 1 (can scale up)
- **Plan**: Starter recommended

### Database Settings
- **PostgreSQL Version**: 15
- **Plan**: Free (1GB) or Starter (10GB)
- **Backups**: Enable (automatic on paid plans)

### Redis Settings
- **MaxMemory Policy**: allkeys-lru
- **Plan**: Free (25MB) or Starter (100MB)

---

## 🐛 TROUBLESHOOTING

### Build Fails: "Command timed out"
**Solution**: Use `requirements-render.txt` instead of `requirements.txt`
```bash
# In build command
pip install -r requirements-render.txt
```

### Build Fails: "ModuleNotFoundError"
**Solution**: Check that package is in requirements-render.txt
```bash
pip install package-name
```

### Runtime Error: "DATABASE_URL not set"
**Solution**: Add DATABASE_URL in Render environment variables
```env
DATABASE_URL=[your-postgres-url]
```

### Worker Not Starting
**Solution**: Check Redis connection
```env
CELERY_BROKER_URL=[your-redis-url]
CELERY_RESULT_BACKEND=[your-redis-url]
```

### "SQLAlchemy" Error
**Solution**: Already fixed in build.sh (SQLAlchemy 2.0 compatible)

---

## 📊 COST ESTIMATE

### Free Tier (Good for Testing)
- Web Service: Free (750 hours/month)
- Worker: Free (750 hours/month)
- PostgreSQL: Free (1GB, expires after 90 days)
- Redis: Free (25MB)
- **Total**: $0/month

### Starter Tier (Production Ready)
- Web Service: $7/month
- Worker: $7/month
- PostgreSQL: $7/month (10GB)
- Redis: $10/month (100MB)
- **Total**: $31/month

### Professional (High Traffic)
- Web Service: $25/month (2GB RAM)
- Worker: $25/month (2GB RAM)
- PostgreSQL: $15/month (50GB)
- Redis: $20/month (500MB)
- **Total**: $85/month

---

## 🔐 SECURITY CHECKLIST

Before deploying:
- [ ] Set strong `FLASK_SECRET_KEY`
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable 2FA on Render account

---

## 📈 POST-DEPLOYMENT

### 1. Verify Deployment
```bash
curl https://your-app.onrender.com/
```

### 2. Test API
```bash
curl -X POST https://your-app.onrender.com/api/analyze \
  -H "X-API-KEY: your-key" \
  -d '{"user_directive": "Test"}'
```

### 3. Monitor Logs
- Go to Render Dashboard
- Click on your service
- View "Logs" tab

### 4. Set Up Custom Domain (Optional)
- Go to Service Settings
- Add custom domain
- Update DNS records

---

## 🎯 QUICK REFERENCE

### Files for Render:
- `render.yaml` - Complete Render config
- `build-render.sh` - Optimized build script
- `requirements-render.txt` - Lighter dependencies
- `Procfile` - Process definitions

### Environment Variables (Required):
```env
DATABASE_URL          # Auto-set by Render
REDIS_URL             # Auto-set by Render
FLASK_SECRET_KEY      # Set manually
GOOGLE_API_KEY        # Set manually
```

### Useful Commands:
```bash
# View logs
render logs [service-name]

# Restart service
render restart [service-name]

# Scale workers
render scale [service-name] --num=2
```

---

## 🆘 NEED HELP?

### Common Issues:
1. **Build timeout**: Use `requirements-render.txt`
2. **Database error**: Check DATABASE_URL is set
3. **Worker not processing**: Check Redis connection
4. **Import errors**: Clear build cache and rebuild

### Render Support:
- [Render Docs](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Render Status](https://status.render.com/)

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Fixed build.sh (SQLAlchemy 2.0)
- [ ] Created requirements-render.txt
- [ ] Created render.yaml
- [ ] Pushed to GitHub
- [ ] Connected to Render
- [ ] Set environment variables
- [ ] Created PostgreSQL database
- [ ] Created Redis instance
- [ ] Deployed web service
- [ ] Deployed worker service
- [ ] Tested API endpoints
- [ ] Verified logs
- [ ] Set up monitoring

---

**🚀 Your CLARITY platform is now deployed on Render!**

**Access**: https://your-app.onrender.com

**Next**: Share API keys with clients via the dashboard!
