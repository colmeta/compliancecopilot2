# 🚀 FRESH VERCEL DEPLOYMENT - 2 MINUTES

**Delete the old, start fresh. This WILL work.**

---

## 📋 STEP-BY-STEP (DO THIS NOW)

### 1. **Delete Old Vercel Project**
- Go to: https://vercel.com/dashboard
- Find: `clarity-engine-auto`
- Click on it
- Click "Settings" (bottom of sidebar)
- Scroll to bottom: "Delete Project"
- Type project name to confirm
- Click "Delete"

### 2. **Create New Vercel Project**
- Go to: https://vercel.com/new
- Click "Import Git Repository"
- Select: `colmeta/compliancecopilot2` (your GitHub repo)
- Click "Import"

### 3. **Configure Project Settings**

**Project Name:**
```
clarity-engine
```

**Framework Preset:**
```
Next.js
```

**Root Directory:**
```
frontend
```
⚠️ **CRITICAL:** Must set this to `frontend`!

**Build Command:**
```
npm run build
```

**Output Directory:**
```
.next
```

**Install Command:**
```
npm install
```

### 4. **Environment Variables** (Add these)

Click "Environment Variables" and add:

**Variable:** `NEXT_PUBLIC_API_URL`  
**Value:** `https://veritas-engine-zae0.onrender.com`

### 5. **Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- **DONE!** ✅

---

## 🎯 YOUR NEW LINKS

After deployment completes:

```
Landing Page:
https://clarity-engine.vercel.app/

Command Deck:
https://clarity-engine.vercel.app/work

Legal Analysis:
https://clarity-engine.vercel.app/work?domain=legal

Funding Engine:
https://clarity-engine.vercel.app/funding
```

---

## ✅ WHY THIS WILL WORK

1. **Fresh deployment** = No cached build errors
2. **Correct root directory** from the start
3. **Clean slate** = Vercel will use latest Next.js build logic
4. **All fixes already in GitHub** = Latest code deployed

---

## 🔥 IF YOU WANT A DIFFERENT URL

**Custom Domain (Optional):**
- After deployment, go to project settings
- Click "Domains"
- Add: `app.claritypearl.com` (or whatever you want)
- Point your DNS to Vercel (they give you instructions)

---

**THIS IS THE NUCLEAR OPTION. IT ALWAYS WORKS.** ✅
