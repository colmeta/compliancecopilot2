# 🔄 Keep-Alive Service Setup Guide

Prevent Render free tier hibernation by setting up a free keep-alive service.

---

## 🎯 Why You Need This

**Render Free Tier Behavior:**
- Services hibernate after **15 minutes of inactivity**
- Takes **30-60 seconds** to wake up
- Causes "Failed to fetch" errors during wake-up

**Keep-Alive Solution:**
- Pings your backend every 5-14 minutes
- Keeps service **always awake**
- **No more hibernation delays!**

---

## 🥇 Option 1: UptimeRobot (Recommended - Easiest)

### Step 1: Create Account
1. Go to: https://uptimerobot.com
2. Click **"Sign Up"** (top right)
3. Create free account (email + password)
4. Verify email if required

### Step 2: Add Monitor
1. After login, click **"+ Add New Monitor"**
2. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `CLARITY Backend Keep-Alive`
   - **URL:** `https://veritas-engine-zae0.onrender.com/health`
   - **Monitoring Interval:** `5 minutes` (free tier allows this)
   - **Alert Contacts:** (Optional - skip for now)
3. Click **"Create Monitor"**

### Step 3: Verify It's Working
1. Wait 1-2 minutes
2. Check monitor status - should show **"Up"** (green)
3. Click on monitor to see response times
4. Your backend will now stay awake 24/7! 🎉

**That's it!** UptimeRobot will ping your backend every 5 minutes automatically.

---

## 🥈 Option 2: Cron-Job.org (Alternative)

### Step 1: Create Account
1. Go to: https://cron-job.org
2. Click **"Sign Up"** (top right)
3. Create free account
4. Verify email

### Step 2: Create Cron Job
1. After login, click **"Create cronjob"**
2. Configure:
   - **Title:** `CLARITY Backend Keep-Alive`
   - **Address:** `https://veritas-engine-zae0.onrender.com/health`
   - **Schedule:** `*/14 * * * *` (every 14 minutes)
   - **Request Method:** GET
   - **Active:** ✅ Checked
3. Click **"Create cronjob"**

### Step 3: Verify
1. Wait 14 minutes
2. Check "Execution Log" - should show successful requests
3. Your backend stays awake! 🎉

---

## 🥉 Option 3: GitHub Actions (Advanced)

If you want to keep it in your repo, use GitHub Actions:

### Create Workflow File
Create: `.github/workflows/keep-alive.yml`

```yaml
name: Keep Backend Alive

on:
  schedule:
    - cron: '*/14 * * * *'  # Every 14 minutes
  workflow_dispatch:  # Allow manual trigger

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Backend
        run: |
          curl -f https://veritas-engine-zae0.onrender.com/health || exit 1
```

### Enable GitHub Actions
1. Push the workflow file to your repo
2. Go to: https://github.com/your-username/compliancecopilot2/actions
3. Enable GitHub Actions if prompted
4. Workflow will run automatically every 14 minutes

---

## 📊 Comparison

| Service | Free Tier | Interval | Setup Time | Best For |
|---------|-----------|----------|------------|----------|
| **UptimeRobot** | ✅ Yes | 5 min | 2 min | ⭐ **Easiest** |
| **Cron-Job.org** | ✅ Yes | 14 min | 3 min | Simple |
| **GitHub Actions** | ✅ Yes | 14 min | 5 min | Developers |

**Recommendation:** Use **UptimeRobot** - it's the easiest and pings more frequently.

---

## ✅ Verification

### Test 1: Check Monitor Status
- UptimeRobot: Dashboard shows "Up" status
- Cron-Job.org: Execution log shows successful requests
- GitHub Actions: Actions tab shows successful runs

### Test 2: Verify Backend Stays Awake
```bash
# Test immediately
curl https://veritas-engine-zae0.onrender.com/health

# Wait 20 minutes, test again
curl https://veritas-engine-zae0.onrender.com/health
```

**Expected:** Both should respond instantly (no 30-60 second delay)

### Test 3: Test Frontend
1. Go to: https://clarity-engine-auto.vercel.app/work
2. Try uploading a document
3. Should work **immediately** (no "Failed to fetch" errors)

---

## 🎯 Quick Setup (UptimeRobot - 2 Minutes)

1. **Sign up:** https://uptimerobot.com
2. **Click:** "+ Add New Monitor"
3. **Type:** HTTP(s)
4. **URL:** `https://veritas-engine-zae0.onrender.com/health`
5. **Interval:** 5 minutes
6. **Click:** "Create Monitor"
7. **Done!** ✅

Your backend will now stay awake 24/7.

---

## 💡 Pro Tips

1. **UptimeRobot Free Tier:**
   - 50 monitors
   - 5-minute intervals
   - Email alerts (optional)
   - Perfect for this use case!

2. **Monitor Multiple Endpoints:**
   - Health: `/health`
   - Instant: `/instant/health`
   - Real: `/real/health`
   - (All ping the same service, but good for redundancy)

3. **Set Up Alerts (Optional):**
   - Get notified if backend goes down
   - Useful for production monitoring

---

## 🚨 Troubleshooting

### Monitor Shows "Down"
- Check if backend URL is correct
- Test manually: `curl https://veritas-engine-zae0.onrender.com/health`
- Backend might be hibernating - wait 30-60 seconds and retry

### Still Getting Hibernation
- Check monitor is actually running (look at execution logs)
- Verify interval is set correctly (5-14 minutes)
- Make sure monitor is "Active" (not paused)

### Want to Stop Keep-Alive
- UptimeRobot: Pause or delete monitor
- Cron-Job.org: Deactivate cronjob
- GitHub Actions: Delete workflow file

---

## ✅ Setup Checklist

- [ ] Created account (UptimeRobot/Cron-Job.org)
- [ ] Added monitor/cronjob
- [ ] Verified monitor is "Up" / cronjob is running
- [ ] Tested backend responds instantly (no delay)
- [ ] Tested frontend works without "Failed to fetch" errors

---

**🎉 Once set up, your backend will stay awake 24/7 and you'll never see "Failed to fetch" errors again!**

