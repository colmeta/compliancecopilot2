# 🐌 Render Free Tier Hibernation Issue

## ❌ The Problem: "Failed to fetch" Errors

You're experiencing **"Failed to fetch. Please try again"** errors because:

### 1. **Render Free Tier Hibernation**
- Render's **free tier** services **spin down after 15 minutes of inactivity**
- When you try to access them, they take **30-60 seconds to "wake up"**
- During this wake-up time, requests fail with "Failed to fetch"

### 2. **URL Mismatch (FIXED ✅)**
- Frontend was using wrong backend URL: `veritas-faxh.onrender.com`
- Correct backend URL: `veritas-engine-zae0.onrender.com`
- **This has been fixed in the code**

### 3. **CORS Issues (FIXED ✅)**
- Added `clarity-engine-auto.vercel.app` to CORS whitelist
- **This has been fixed in the code**

---

## ✅ What I Fixed

1. **Frontend Backend URL** - Changed from `veritas-faxh` to `veritas-engine-zae0`
2. **CORS Configuration** - Added your Vercel domain to allowed origins
3. **Better Error Messages** - Now shows helpful message about Render hibernation

---

## 🔧 Solutions for Render Hibernation

### Option 1: Wait and Retry (Free)
- When you get "Failed to fetch", **wait 30-60 seconds**
- The backend is waking up
- Then try your request again
- **This is normal for Render free tier**

### Option 2: Keep-Alive Service (Free)
Use a free uptime monitoring service to ping your backend every 14 minutes:

**Recommended: UptimeRobot (Free)**
1. Go to: https://uptimerobot.com
2. Create account (free)
3. Add monitor:
   - Type: HTTP(s)
   - URL: `https://veritas-engine-zae0.onrender.com/health`
   - Interval: 5 minutes (free tier allows this)
4. This will keep your backend awake 24/7

**Alternative: Cron-Job.org (Free)**
1. Go to: https://cron-job.org
2. Create account
3. Add job:
   - URL: `https://veritas-engine-zae0.onrender.com/health`
   - Schedule: Every 14 minutes
   - Method: GET

### Option 3: Upgrade Render Plan ($7/month)
- Render Starter plan: **$7/month**
- Services **never hibernate**
- Always available, instant responses
- No "Failed to fetch" errors

---

## 🧪 How to Test if Backend is Working

### Test 1: Check if Backend is Awake
```bash
curl https://veritas-engine-zae0.onrender.com/health
```

**Expected Response:**
- If awake: `{"status": "ok", ...}` (instant)
- If hibernating: Takes 30-60 seconds, then responds

### Test 2: Test Legal Analysis
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Test legal analysis", "domain": "legal"}'
```

---

## 📊 Current Status

**Backend URL:** `https://veritas-engine-zae0.onrender.com` ✅  
**Frontend URL:** `https://clarity-engine-auto.vercel.app` ✅  
**CORS:** Configured ✅  
**Hibernation:** Active (Render free tier) ⚠️  

---

## 🚀 Next Steps

1. **Deploy the fixes** (URL and CORS changes)
2. **Set up UptimeRobot** (free, keeps backend awake)
3. **Test again** - should work after backend wakes up

---

## 💡 Why This Happens

Render's free tier is designed for:
- Development/testing
- Low-traffic projects
- Non-critical applications

For production apps, you need:
- Keep-alive service (free option)
- Or paid Render plan ($7/month)

**The app IS working** - it just needs to wake up first! 🎯

