# 🚂 DEPLOY TO RAILWAY - 3 MINUTES

**Alternative: Deploy ENTIRE app (frontend + backend) in one place**

---

## 🎯 WHY RAILWAY?

✅ **Deploys Next.js + Flask together**
✅ **No separate frontend/backend hosting**
✅ **Free tier: $5/month credit**
✅ **Automatic HTTPS**
✅ **One dashboard for everything**

---

## 📋 STEP-BY-STEP

### 1. **Create Railway Account**
- Go to: https://railway.app/
- Click "Login" → Sign in with GitHub

### 2. **Create New Project**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Authorize Railway
- Select: `colmeta/compliancecopilot2`

### 3. **Configure Frontend Service**

Railway will auto-detect both frontend and backend. We'll deploy BOTH.

**For Frontend:**
- Click "New Service" → "GitHub Repo"
- Select your repo
- Click "Settings"
- Set Root Directory: `frontend`
- Set Build Command: `npm run build`
- Set Start Command: `npm start`

**Environment Variables:**
```
NEXT_PUBLIC_API_URL = https://your-backend-url.railway.app
```
(You'll get this URL after deploying backend)

### 4. **Configure Backend Service**

- Click "New Service" → "GitHub Repo"  
- Select same repo again
- Set Root Directory: `/` (root)
- Set Start Command: `gunicorn run:app`

**Environment Variables:**
(Copy all from Render - especially GOOGLE_API_KEY)

### 5. **Deploy**
- Both services deploy automatically
- Wait 3-5 minutes
- **DONE!** ✅

---

## 🎯 YOUR NEW SETUP

```
Frontend: https://clarity-frontend-production.railway.app/
Backend:  https://clarity-backend-production.railway.app/

Full Command Deck:
https://clarity-frontend-production.railway.app/work
```

---

## 💰 COST

**Free Tier:**
- $5/month credit (auto-renewed)
- Enough for small-medium traffic
- Can add payment method for more

**Paid:**
- Pay-as-you-go
- ~$10-20/month for both services

---

## 🔥 ADVANTAGES OVER VERCEL + RENDER

✅ **Everything in one place**
✅ **No CORS issues** (can use internal networking)
✅ **Easier to manage**
✅ **Better for full-stack apps**

---

## 🚨 DOWNSIDE

❌ **Costs money after $5 credit** (but cheap)
❌ **Not as fast as Vercel CDN** (but still fast)

---

**RAILWAY IS BEST IF YOU WANT ONE PLATFORM FOR EVERYTHING.** ✅
