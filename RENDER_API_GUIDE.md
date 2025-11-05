# 🚀 Deploy CLARITY Using Render API

## Automated Deployment with Python Script

I've created **`deploy-to-render.py`** - a Python script that uses the Render API to automatically deploy CLARITY.

---

## 🔑 Getting Your Render API Key

### Step 1: Go to Render Dashboard
1. Visit https://dashboard.render.com/
2. Log in to your account (or create one if needed)

### Step 2: Generate API Key
1. Click your **profile picture** (top right)
2. Select **"Account Settings"**
3. Go to **"API Keys"** tab
4. Click **"Create API Key"**
5. Give it a name: `CLARITY Deployment`
6. **Copy the key** (starts with `rnd_...`)

### Step 3: Set Environment Variable
```bash
export RENDER_API_KEY='rnd_your_api_key_here'
```

---

## 🚀 Using the Automated Deployment Script

### Quick Deploy (All-in-One)
```bash
# Set your credentials
export RENDER_API_KEY='rnd_your_api_key_here'
export GITHUB_REPO_URL='https://github.com/yourusername/clarity'
export GOOGLE_API_KEY='your-gemini-key-here'
export FLASK_SECRET_KEY='your-secret-key'

# Optional (multi-LLM failover)
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-claude-key'
export GROQ_API_KEY='your-groq-key'

# Run deployment
python deploy-to-render.py
```

### What the Script Does:
1. ✅ Tests Render API connection
2. ✅ Creates PostgreSQL database
3. ✅ Creates Redis instance
4. ✅ Creates web service
5. ✅ Creates background worker
6. ✅ Configures all environment variables
7. ✅ Starts deployment

**Takes**: 5-8 minutes for complete deployment

---

## 📋 Manual Alternative (If Script Fails)

### Using Render Dashboard:

1. **Create PostgreSQL Database**
   - New → PostgreSQL
   - Name: `clarity-db`
   - Plan: Starter ($7/month) or Free
   - Copy Internal Connection String

2. **Create Redis Instance**
   - New → Redis
   - Name: `clarity-redis`
   - Plan: Starter ($10/month) or Free
   - Copy Internal Connection String

3. **Create Web Service**
   - New → Web Service
   - Connect GitHub repo
   - Build: `./build-render.sh`
   - Start: `gunicorn run:app --bind 0.0.0.0:$PORT`
   - Add all environment variables

4. **Create Background Worker**
   - New → Background Worker
   - Same repo
   - Build: `./build-render.sh`
   - Start: `celery -A celery_worker.celery_app worker`
   - Add same environment variables

---

## 🔍 Checking Deployment Status

### Via Render API:
```bash
curl https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Via Dashboard:
1. Go to https://dashboard.render.com/
2. Click on each service
3. View "Logs" tab for build progress

---

## 🐛 Troubleshooting

### "RENDER_API_KEY not set"
**Solution**: Export your API key:
```bash
export RENDER_API_KEY='rnd_your_key_here'
```

### "GITHUB_REPO_URL not set"
**Solution**: Set your GitHub repository:
```bash
export GITHUB_REPO_URL='https://github.com/yourusername/clarity'
```

### "API connection failed"
**Solution**: 
- Check API key is correct
- Verify internet connection
- Try regenerating API key in Render dashboard

### "Build timeout"
**Solution**: Script uses `requirements-render.txt` automatically (optimized)

---

## 💰 Cost Breakdown

When using the automated script with default settings:

- PostgreSQL (Starter): $7/month
- Redis (Starter): $10/month
- Web Service (Starter): $7/month
- Background Worker (Starter): $7/month

**Total**: $31/month

To use **Free Tier**, modify the script:
```python
# In deploy-to-render.py, change:
"plan": "starter"  # to "plan": "free"
```

---

## 📞 I Don't Have Your Render API Key

**Important**: I cannot access your Render account or API key for security reasons.

**You have 2 options:**

### Option 1: Run the Script Yourself (Recommended)
```bash
# Get your Render API key from dashboard
export RENDER_API_KEY='your-key'
export GITHUB_REPO_URL='your-repo'
export GOOGLE_API_KEY='your-gemini-key'

# Run the automated script
python deploy-to-render.py
```

### Option 2: Use render.yaml (Blueprint)
```bash
# Push to GitHub
git push origin main

# In Render Dashboard:
# 1. New → Blueprint
# 2. Select your repo
# 3. Render auto-detects render.yaml
# 4. Set environment variables
# 5. Click Apply
```

---

## ✅ What I've Done for You

1. ✅ **Fixed all build issues** (SQLAlchemy 2.0, dependencies)
2. ✅ **Created automated deployment script** (`deploy-to-render.py`)
3. ✅ **Created render.yaml** (Blueprint configuration)
4. ✅ **Created requirements-render.txt** (Optimized dependencies)
5. ✅ **Created build-render.sh** (Optimized build script)
6. ✅ **Complete documentation** (this guide + RENDER_DEPLOYMENT.md)

---

## 🎯 Next Steps

1. **Get your Render API key** (see instructions above)
2. **Run the deployment script**:
   ```bash
   python deploy-to-render.py
   ```
3. **Wait 5-8 minutes** for build to complete
4. **Access your platform**: https://your-app.onrender.com
5. **Generate API keys** for clients
6. **Start using CLARITY!**

---

**Need help?** Let me know your Render API key or I can walk you through manual deployment!
