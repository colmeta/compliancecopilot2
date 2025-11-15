# 🔧 FIX: Update Vercel Environment Variable

## The Problem:
Your frontend code has the correct URL (`veritas-faxh.onrender.com`), but Vercel has an environment variable `NEXT_PUBLIC_API_URL` set to the OLD URL (`veritas-engine-zae0.onrender.com`).

**Environment variables override code defaults**, so Vercel is using the old URL.

## The Fix (2 Minutes):

### Step 1: Go to Vercel Dashboard
1. Go to: https://vercel.com/dashboard
2. Find your project: `clarity-engine-auto` (or similar)
3. Click on it

### Step 2: Update Environment Variable
1. Go to **Settings** tab
2. Click **Environment Variables** (left sidebar)
3. Find: `NEXT_PUBLIC_API_URL`
4. **Change value from:**
   ```
   https://veritas-engine-zae0.onrender.com
   ```
   **To:**
   ```
   https://veritas-faxh.onrender.com
   ```
5. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click the **3 dots** (⋯) on the latest deployment
3. Click **Redeploy**
4. Wait 1-2 minutes

## That's It!

After redeploy, your frontend will use the correct backend URL and the CORS error will be fixed.

---

## Why This Happened:
- Code default: `veritas-faxh.onrender.com` ✅
- Vercel env var: `veritas-engine-zae0.onrender.com` ❌
- **Env var wins** → Frontend uses old URL → CORS error

## After Fix:
- Frontend will use: `veritas-faxh.onrender.com` ✅
- CORS is already configured for this domain ✅
- Everything will work! ✅

