# 🚨 Backend 502 Error - Service Down

## What Happened:
You're getting a **502 Bad Gateway** error, which means:
- The backend service on Render is **down or crashed**
- This is **NOT related to frontend changes** - it's a backend server issue

## Quick Fixes:

### 1. Check Render Dashboard
1. Go to: https://dashboard.render.com
2. Find your service: `veritas-faxh`
3. Check the **Status** - is it showing as "Live" or "Failed"?
4. Check the **Logs** tab - what errors do you see?

### 2. Restart the Service
1. In Render dashboard, click on your service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Or click **Restart** if available
4. Wait 2-3 minutes for it to come back up

### 3. Check Service Logs
Look for errors like:
- Out of memory
- Python errors
- Import errors
- Port binding issues

## Common Causes:

### 1. Service Crashed
- Application error
- Out of memory
- Python exception

### 2. Service Restarting
- Render is restarting the service
- Wait 1-2 minutes

### 3. Deployment Failed
- Build error
- Dependency issue
- Configuration problem

## What to Do:

1. **Check Render Dashboard** - See what's happening
2. **Check Logs** - Find the error
3. **Restart Service** - If it's stuck
4. **Check Recent Deployments** - See if a deployment failed

## If Service Won't Start:

Check for:
- Python syntax errors
- Missing dependencies
- Environment variable issues
- Port conflicts

## Status Check:
Once the service is back up, test:
```
https://veritas-faxh.onrender.com/health
```

Should return: `{"status": "ok", ...}`

---

**The frontend changes are fine - this is a backend service issue on Render.**

