# ⚡ Quick Start - Fix "Failed to Fetch" Errors

## 🎯 What Was Fixed

✅ Backend URL corrected  
✅ CORS configured for Vercel  
✅ Better error messages  
✅ Changes committed & pushed  

---

## 🚀 Deploy Now (5 Minutes)

### 1. Backend (Render) - Auto-Deploying
- ✅ Changes pushed to `main` branch
- ⏳ Render will auto-deploy in 2-5 minutes
- 🔍 Check: https://dashboard.render.com → `veritas-engine-zae0`

### 2. Frontend (Vercel) - Auto-Deploying
- ✅ Changes pushed to `main` branch  
- ⏳ Vercel will auto-deploy in 1-2 minutes
- 🔍 Check: https://vercel.com/dashboard → Your project

### 3. Verify Deployment
```bash
# Test backend
curl https://veritas-engine-zae0.onrender.com/health

# Should return: {"status": "ok", ...}
```

---

## 🔄 Set Up Keep-Alive (2 Minutes)

### UptimeRobot (Easiest)

1. **Go to:** https://uptimerobot.com
2. **Sign up** (free)
3. **Click:** "+ Add New Monitor"
4. **Configure:**
   - Type: HTTP(s)
   - URL: `https://veritas-engine-zae0.onrender.com/health`
   - Interval: 5 minutes
5. **Click:** "Create Monitor"
6. **Done!** ✅

Your backend will stay awake 24/7!

---

## ✅ Test Everything Works

1. **Wait 5 minutes** for deployments
2. **Go to:** https://clarity-engine-auto.vercel.app/work
3. **Try:** Upload document or run analysis
4. **Expected:** Should work (or show helpful hibernation message)

---

## 📚 Full Guides

- **Deployment:** See `DEPLOYMENT_GUIDE.md`
- **Keep-Alive:** See `KEEP_ALIVE_SETUP.md`
- **Issue Details:** See `RENDER_FREE_TIER_ISSUE.md`

---

## 🆘 Still Having Issues?

1. **Backend hibernating?** → Set up keep-alive (above)
2. **CORS errors?** → Wait for backend deployment
3. **Wrong URL?** → Clear browser cache (Ctrl+Shift+Delete)

---

**🎉 Once keep-alive is set up, you'll never see "Failed to fetch" errors again!**

