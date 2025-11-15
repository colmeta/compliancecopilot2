# 🚨 URGENT: Fix Vercel Environment Variable

## The Problem:
Your frontend is STILL calling the old URL: `veritas-engine-zae0.onrender.com`
It should be calling: `veritas-faxh.onrender.com`

## Step-by-Step Fix:

### Step 1: Update Vercel Environment Variable
1. Go to: https://vercel.com/dashboard
2. Click on your project: `clarity-engine-auto`
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)
5. Find `NEXT_PUBLIC_API_URL` in the list
6. Click the **pencil icon** (edit) next to it
7. **Delete the old value** and **type the new one:**
   ```
   https://veritas-faxh.onrender.com
   ```
8. Make sure it's set for **Production**, **Preview**, and **Development**
9. Click **Save**

### Step 2: Redeploy (CRITICAL!)
1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **3 dots** (⋯) on the right
4. Click **Redeploy**
5. Select **Use existing Build Cache** = NO (uncheck it)
6. Click **Redeploy**
7. **Wait 2-3 minutes** for deployment to complete

### Step 3: Clear Browser Cache
1. Open your site: https://clarity-engine-auto.vercel.app
2. Press **Ctrl + Shift + Delete** (Windows) or **Cmd + Shift + Delete** (Mac)
3. Select **Cached images and files**
4. Click **Clear data**
5. **Hard refresh** the page: **Ctrl + F5** (Windows) or **Cmd + Shift + R** (Mac)

### Step 4: Verify It's Fixed
1. Open browser console (F12)
2. Go to **Network** tab
3. Try uploading a document
4. Check the request URL - it should be:
   ```
   https://veritas-faxh.onrender.com/instant/analyze
   ```
   NOT:
   ```
   https://veritas-engine-zae0.onrender.com/instant/analyze
   ```

## If It Still Doesn't Work:

### Check Environment Variable Was Saved:
1. Go back to Vercel → Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` shows: `https://veritas-faxh.onrender.com`
3. If it still shows the old URL, update it again

### Force Clear Build Cache:
1. In Vercel, go to **Deployments**
2. Click **3 dots** → **Redeploy**
3. **Uncheck** "Use existing Build Cache"
4. This forces a fresh build with the new env var

### Check Deployment Logs:
1. Click on the deployment
2. Check **Build Logs**
3. Look for: `NEXT_PUBLIC_API_URL`
4. It should show: `https://veritas-faxh.onrender.com`

## Why This Happens:
- Next.js bakes environment variables into the JavaScript at **build time**
- If you update the env var but don't redeploy, the old URL stays in the code
- Browser cache can also serve old JavaScript files

## After Fix:
✅ Frontend will call: `veritas-faxh.onrender.com`
✅ CORS is already configured for this domain
✅ Everything will work!

