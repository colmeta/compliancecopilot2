# CLARITY Engine - Complete Environment Variables Guide

## 🎯 FOR TESTING THE COMPLETE PLATFORM

This is the **complete list** of environment variables needed to unlock **ALL** features of the CLARITY Engine.

---

## 📋 REQUIRED (Core Functionality)

### **Database**
```bash
# PostgreSQL connection (Render provides this automatically)
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### **Secret Key**
```bash
# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_super_secret_key_here_at_least_32_characters_long
```

### **Google AI (Primary LLM)**
```bash
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=AIzaSyDG3rF4Ghl966JuVLTliwKagnkPNZmVPpA
```

---

## 🚀 RECOMMENDED (Multi-LLM Failover System)

### **OpenAI (GPT-4)**
```bash
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **Anthropic (Claude)**
```bash
# Get from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **Groq (Fast Inference)**
```bash
# Get from: https://console.groq.com/keys
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Why:** With all 4 LLMs configured, CLARITY will:
- **Never fail** (automatic failover)
- Route complex tasks to GPT-4/Claude
- Route fast tasks to Gemini/Groq
- Optimize cost vs. quality automatically

---

## 🎙️ OPTIONAL (Multi-Modal Features)

### **Audio Transcription (Pro Tier)**
```bash
# Google Cloud Speech-to-Text
GOOGLE_SPEECH_API_KEY=your_google_cloud_key_here

# AssemblyAI (specialized, high accuracy)
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
```

### **Vision/OCR (Document Scanning)**
```bash
# Google Cloud Vision API
GOOGLE_VISION_API_KEY=your_google_vision_key_here

# AWS Textract (enterprise OCR)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

**Why:** Without these, CLARITY uses **free, local alternatives** (Whisper for audio, Tesseract for OCR). 
With these, you get **enterprise-grade accuracy** for Pro/Enterprise tiers.

---

## 🔐 OPTIONAL (Enterprise Security & Compliance)

### **Redis (Caching & Real-Time Collaboration)**
```bash
# Redis connection (Render provides this automatically if you add Redis)
REDIS_URL=redis://username:password@host:6379

# For WebSocket collaboration
SOCKETIO_MESSAGE_QUEUE=redis://username:password@host:6379/2
```

### **Email (User Notifications)**
```bash
# SMTP server for sending emails
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_specific_password
```

### **Sentry (Error Monitoring)**
```bash
# Get from: https://sentry.io
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

---

## ⚙️ FEATURE FLAGS (Turn Features On/Off)

### **Outstanding Writing System**
```bash
# Enable the 5-pass presidential-grade writing system
ENABLE_OUTSTANDING_MODE=true

# Use it for specific domains (comma-separated)
OUTSTANDING_DOMAINS=legal,financial,funding,security,proposal
```

### **AI Optimization**
```bash
# Enable intelligent model routing
ENABLE_MODEL_ROUTING=true
DEFAULT_MODEL=gemini-1.5-flash

# Enable response caching (saves cost + speed)
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_SECONDS=3600
```

### **Compliance & Audit Logging**
```bash
# Enable audit logging for all actions
ENABLE_AUDIT_LOGGING=true

# Enable automatic PII detection
ENABLE_PII_DETECTION=true

# Data retention (7 years for legal compliance)
DATA_RETENTION_DAYS=2555
```

### **Tier System**
```bash
# Default tier for new users
DEFAULT_TIER=free

# Enable tier-based features
ENFORCE_TIER_LIMITS=true
```

---

## 🎯 FRONTEND ENVIRONMENT VARIABLES

Create a file: `frontend/.env.local`

```bash
# Point to your backend API
NEXT_PUBLIC_API_URL=https://veritas-engine.onrender.com

# For local development:
# NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 📝 HOW TO SET ENVIRONMENT VARIABLES

### **Local Development (.env file)**
Create a `.env` file in the root directory:

```bash
# Copy from .env.example
cp .env.example .env

# Edit with your keys
nano .env
```

### **Render (Production)**
1. Go to: https://dashboard.render.com/web/srv-your-service-id
2. Click **"Environment"** tab
3. Add each variable as **"Key"** and **"Value"**
4. Click **"Save Changes"**
5. Render will **auto-redeploy**

### **Vercel (Frontend)**
1. Go to: https://vercel.com/your-username/clarity-frontend/settings/environment-variables
2. Add: `NEXT_PUBLIC_API_URL`
3. Set value to: `https://veritas-engine.onrender.com`
4. Click **"Save"**
5. **Redeploy** from the Deployments tab

---

## 🧪 TESTING CHECKLIST

### **Minimal Setup (Core Features Only)**
✅ `DATABASE_URL` (Render provides automatically)  
✅ `SECRET_KEY` (generate one)  
✅ `GOOGLE_API_KEY` (you already have this)  

**Result:** Basic CLARITY works. Single LLM (Gemini). Text documents only.

---

### **Recommended Setup (Full Platform)**
✅ All Minimal Setup variables  
✅ `OPENAI_API_KEY` (for GPT-4 failover)  
✅ `ANTHROPIC_API_KEY` (for Claude failover)  
✅ `GROQ_API_KEY` (for fast inference)  
✅ `ENABLE_OUTSTANDING_MODE=true` (for presidential-grade writing)  
✅ `ENABLE_RESPONSE_CACHE=true` (for speed + cost savings)  

**Result:** Full multi-LLM system. Outstanding Writing. Never fails. Fast and smart.

---

### **Enterprise Setup (All Features Unlocked)**
✅ All Recommended Setup variables  
✅ `REDIS_URL` (for caching + collaboration)  
✅ `GOOGLE_SPEECH_API_KEY` or `ASSEMBLYAI_API_KEY` (for audio transcription)  
✅ `GOOGLE_VISION_API_KEY` (for high-accuracy OCR)  
✅ `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` (for email notifications)  
✅ `ENABLE_AUDIT_LOGGING=true` (for compliance)  

**Result:** Full presidential-grade platform. Multi-modal. Compliant. Enterprise-ready.

---

## 🔑 WHERE TO GET API KEYS (Quick Links)

| Service | Sign Up Link | Free Tier? |
|---------|--------------|------------|
| **Google Gemini** | https://makersuite.google.com/app/apikey | ✅ Yes (60 req/min) |
| **OpenAI GPT-4** | https://platform.openai.com/api-keys | 💰 $5 minimum credit |
| **Anthropic Claude** | https://console.anthropic.com/settings/keys | 💰 Pay as you go |
| **Groq** | https://console.groq.com/keys | ✅ Yes (very generous) |
| **AssemblyAI** | https://www.assemblyai.com/dashboard/signup | ✅ Yes (free hours) |
| **Google Cloud Vision** | https://console.cloud.google.com/apis/credentials | ✅ Yes (1000 req/month) |
| **AWS Textract** | https://aws.amazon.com/textract/ | ✅ Yes (free tier) |

---

## 💡 PRO TIPS

### **1. Start Small, Scale Up**
- Week 1: Just `GOOGLE_API_KEY` (test core features)
- Week 2: Add OpenAI + Anthropic (test failover)
- Week 3: Add audio/vision keys (test multi-modal)

### **2. Monitor Your Costs**
- **Gemini:** Basically free for testing
- **GPT-4:** ~$0.01 per analysis (set a $10 limit initially)
- **Claude:** Similar to GPT-4
- **Groq:** Free and FAST

### **3. Use Feature Flags**
Don't enable everything at once. Enable features as you test them:
```bash
# Start with this
ENABLE_OUTSTANDING_MODE=false
ENABLE_MODEL_ROUTING=false

# Enable once basic tests pass
ENABLE_OUTSTANDING_MODE=true
ENABLE_MODEL_ROUTING=true
```

### **4. Check Backend Health**
After setting variables on Render, verify they loaded:
```bash
curl https://veritas-engine.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "llm_configured": ["gemini", "openai", "anthropic", "groq"],
  "features": {
    "outstanding_mode": true,
    "model_routing": true,
    "caching": true
  }
}
```

---

## 🚨 COMMON ISSUES

### **"LLM not configured" error**
- Check that `GOOGLE_API_KEY` is set correctly in Render
- Render may need a manual redeploy after adding env vars

### **Frontend can't reach backend**
- Check `NEXT_PUBLIC_API_URL` in Vercel
- Make sure backend is live: `curl https://veritas-engine.onrender.com/`

### **"Payment required" for OpenAI/Anthropic**
- These require a credit card and minimum deposit
- Start with just Gemini + Groq (both free)

### **Backend slow or timing out**
- Enable `REDIS_URL` for caching
- Set `ENABLE_RESPONSE_CACHE=true`

---

## 📞 NEED HELP?

**Email:** nsubugacollin@gmail.com  
**Phone:** +256 705 885 118  

---

## ✅ QUICK START COMMANDS

### **1. Clone & Setup Local Environment**
```bash
git clone https://github.com/YOUR_USERNAME/clarity-engine.git
cd clarity-engine
cp .env.example .env
# Edit .env with your keys
pip install -r requirements.txt
flask run
```

### **2. Setup Frontend**
```bash
cd frontend
cp .env.local.example .env.local
# Edit .env.local (set NEXT_PUBLIC_API_URL)
npm install
npm run dev
```

### **3. Test Everything**
- Backend: http://localhost:5000/health
- Frontend: http://localhost:3000
- API Docs: http://localhost:5000/api/docs

---

**Remember:** You already have a **working backend** on Render with `GOOGLE_API_KEY`. 
Add the other keys **one at a time** to test each feature incrementally.

🚀 **Now go test your empire!**
