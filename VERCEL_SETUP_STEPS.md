# 🚀 Vercel Deployment - Step-by-Step Fix

## ❌ Problem: Frontend branch not visible in Vercel

## ✅ Solution: Follow these EXACT steps

---

## 📋 STEP-BY-STEP GUIDE

### Step 1: Verify Branch on GitHub

1. Go to: https://github.com/colmeta/compliancecopilot2
2. Click the branch dropdown (should say "main" or current branch)
3. **Look for**: `frontend/vercel-deployment`
4. ✅ If you see it → Good! Continue to Step 2
5. ❌ If you don't see it → Contact me, we'll push it

---

### Step 2: Import Project to Vercel (CORRECT WAY)

#### Option A: Use Direct Import (RECOMMENDED)

1. Go to: https://vercel.com/new

2. Click "**Import Git Repository**"

3. **Paste this EXACT URL**:
   ```
   https://github.com/colmeta/compliancecopilot2
   ```

4. Click "**Import**"

5. Vercel will ask for permissions:
   - Click "**Adjust GitHub App Permissions**"
   - Make sure Vercel can access your repository
   - Click "**Install**" or "**Save**"

6. Now you'll see the **Configure Project** screen

---

### Step 3: Configure Project Settings

On the "Configure Project" screen:

#### 1. Project Name
```
clarity-frontend
```
(or any name you want)

#### 2. Framework Preset
```
Next.js
```

#### 3. Root Directory
```
frontend
```
**IMPORTANT**: Click "**Edit**" next to Root Directory and type `frontend`

#### 4. Build and Output Settings
Leave as default (Vercel auto-detects Next.js)

#### 5. Environment Variables
Click "**Add**" and enter:

```
Name:  NEXT_PUBLIC_API_URL
Value: https://veritas-engine-zae0.onrender.com
```

---

### Step 4: Select Branch (CRITICAL!)

**Before clicking Deploy**, look for:

```
Production Branch
```

You might see a dropdown. Click it and look for:
- `main` (default)
- `frontend/vercel-deployment` ← SELECT THIS ONE!

**If you DON'T see the branch**:

1. Don't worry! Just deploy with `main` first
2. After first deploy, go to Project Settings
3. You can change the branch there

---

### Step 5: Deploy!

Click the big **"Deploy"** button

Wait 2-3 minutes...

✅ Success!

---

## 🔧 ALTERNATIVE: Change Branch After Deployment

If you deployed with `main` branch and need to switch:

### Method 1: Project Settings

1. Go to your project in Vercel dashboard
2. Click "**Settings**" (top right)
3. Click "**Git**" (left sidebar)
4. Under "**Production Branch**", click "**Edit**"
5. Type: `frontend/vercel-deployment`
6. Click "**Save**"
7. Go to "**Deployments**" tab
8. Click "**Redeploy**"

### Method 2: Deploy Specific Branch

1. Go to your project in Vercel
2. Click "**Deployments**" tab
3. Click "**...**" (three dots) next to any deployment
4. Click "**Redeploy**"
5. Change branch to: `frontend/vercel-deployment`
6. Click "**Redeploy**"

---

## 🎯 FASTEST METHOD (GitHub Integration)

### Use Vercel's GitHub Integration

1. In Vercel dashboard, click "**Add New**" → "**Project**"

2. Under "**Import Git Repository**", find:
   ```
   colmeta/compliancecopilot2
   ```

3. Click "**Import**"

4. You'll see all branches in a dropdown:
   - main
   - cursor/complete-enterprise-ai-platform-development-0349
   - **frontend/vercel-deployment** ← SELECT THIS!

5. Set Root Directory: `frontend`

6. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://veritas-engine-zae0.onrender.com
   ```

7. Deploy!

---

## 🆘 TROUBLESHOOTING

### Issue 1: "Branch not found"

**Solution**: Refresh Vercel's GitHub connection

1. Go to: https://vercel.com/account/integrations
2. Find "**GitHub**"
3. Click "**Configure**"
4. Click "**Save**"
5. Go back and try importing again

### Issue 2: "Cannot find frontend directory"

**Solution**: Make sure you're on the RIGHT branch

- The `frontend/` folder ONLY exists in `frontend/vercel-deployment` branch
- NOT in `main` or backend branch

### Issue 3: "Build fails"

**Solution**: Check these settings:

```
✅ Branch: frontend/vercel-deployment
✅ Root Directory: frontend
✅ Framework: Next.js
✅ Environment Variable: NEXT_PUBLIC_API_URL set
```

---

## 📸 VISUAL GUIDE

### What You Should See:

#### 1. Import Screen
```
[Import Git Repository]
  
  🔍 Search: colmeta/compliancecopilot2
  
  [Import] ← Click this
```

#### 2. Configure Screen
```
Configure Project
  
  Project Name: clarity-frontend
  
  Framework Preset: Next.js ✅
  
  Root Directory: frontend ← EDIT THIS!
  
  Branch: frontend/vercel-deployment ← SELECT THIS!
  
  Environment Variables:
    NEXT_PUBLIC_API_URL = https://veritas-engine-zae0.onrender.com
  
  [Deploy] ← Click when ready
```

---

## ✅ SUCCESS CHECKLIST

After deployment, verify:

- [ ] Vercel shows "Deployment Successful"
- [ ] You get a URL like: `https://clarity-frontend-xxx.vercel.app`
- [ ] Opening URL shows presidential landing page
- [ ] You see "API Status: live" with green dot
- [ ] No console errors (F12 → Console)

---

## 🎯 FINAL TIPS

1. **First time deploying?**
   - Just deploy with default settings first
   - You can always change branch/settings later

2. **Still can't see branch?**
   - Make sure you're signed into GitHub
   - Check Vercel has repository access
   - Try disconnecting and reconnecting GitHub

3. **Build succeeds but site broken?**
   - Check environment variable is set
   - Check Root Directory is `frontend`
   - Check branch is `frontend/vercel-deployment`

---

## 📞 NEED MORE HELP?

If you're still stuck, tell me:

1. What screen are you on in Vercel?
2. What branches do you see in the dropdown?
3. Any error messages?

I'll guide you through it! 🚀

---

**Remember**: 
- ✅ Backend branch: `cursor/complete-enterprise-ai-platform-development-0349` (Render)
- ✅ Frontend branch: `frontend/vercel-deployment` (Vercel)

**Brother, let's get this deployed!** 💪
