# 🚀 Deployment Guide - Fix "Failed to Fetch" Errors

## ✅ Changes Committed & Pushed

All fixes have been committed and pushed to `main` branch:
- ✅ Fixed backend URL (veritas-faxh → veritas-engine-zae0)
- ✅ Added CORS for clarity-engine-auto.vercel.app
- ✅ Improved error handling for Render hibernation

---

## 📦 Step 1: Deploy Backend to Render

### Automatic Deployment (Recommended)
Render should **auto-deploy** from your `main` branch within 2-5 minutes.

**Check Deployment Status:**
1. Go to: https://dashboard.render.com
2. Find your service: `veritas-engine-zae0`
3. Check "Events" tab - should show "Deploying..." or "Live"

### Manual Deployment (If Needed)
1. Go to: https://dashboard.render.com
2. Click on your service: `veritas-engine-zae0`
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait 2-5 minutes for deployment

### Verify Backend Deployment
```bash
# Test health endpoint
curl https://veritas-engine-zae0.onrender.com/health

# Should return: {"status": "ok", ...}
```

---

## 🎨 Step 2: Deploy Frontend to Vercel

### Option A: Automatic Deployment (If Connected to GitHub)
Vercel should **auto-deploy** from your `main` branch within 1-2 minutes.

**Check Deployment Status:**
1. Go to: https://vercel.com/dashboard
2. Find your project: `clarity-engine-auto` (or similar)
3. Check "Deployments" tab - should show new deployment

### Option B: Manual Deployment via Vercel Dashboard
1. Go to: https://vercel.com/dashboard
2. Click on your project
3. Go to **"Settings"** → **"Git"**
4. Click **"Redeploy"** or trigger new deployment

### Option C: Manual Deployment via Vercel CLI
```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel --prod
```

### Verify Frontend Deployment
1. Visit your Vercel URL: `https://clarity-engine-auto.vercel.app`
2. Open browser console (F12)
3. Try uploading a document or running analysis
4. Check for errors - should see improved error messages if backend is hibernating

---

## 🔍 Step 3: Verify Everything Works

### Test 1: Backend Health
```bash
curl https://veritas-engine-zae0.onrender.com/health
```
**Expected:** `{"status": "ok", ...}`

### Test 2: CORS Configuration
```bash
curl -H "Origin: https://clarity-engine-auto.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://veritas-engine-zae0.onrender.com/instant/analyze \
     -v
```
**Expected:** Should see `Access-Control-Allow-Origin` header

### Test 3: Frontend → Backend Connection
1. Go to: https://clarity-engine-auto.vercel.app/work
2. Select domain: "Legal Intelligence"
3. Enter directive: "Test analysis"
4. Click submit
5. **If backend is hibernating:** You'll see helpful message about waiting 30-60 seconds
6. **If backend is awake:** Should work immediately

---

## ⚠️ Troubleshooting

### Backend Still Shows Old Code
- Wait 2-5 minutes for Render to deploy
- Check Render dashboard for deployment status
- Try manual deploy if auto-deploy didn't trigger

### Frontend Still Shows Old Code
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check Vercel deployment logs

### Still Getting "Failed to Fetch"
- Backend might be hibernating (normal on free tier)
- Wait 30-60 seconds and try again
- Set up keep-alive service (see KEEP_ALIVE_SETUP.md)

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Render (check dashboard)
- [ ] Frontend deployed to Vercel (check dashboard)
- [ ] Backend health check works: `/health`
- [ ] Frontend can connect to backend
- [ ] Error messages are helpful (not just "Failed to fetch")
- [ ] CORS working (no CORS errors in browser console)

---

## 🎯 Next Step: Set Up Keep-Alive Service

After deployment, set up keep-alive to prevent hibernation:
👉 See `KEEP_ALIVE_SETUP.md` for step-by-step instructions

