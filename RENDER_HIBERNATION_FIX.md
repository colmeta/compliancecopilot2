# 🔧 RENDER HIBERNATION ISSUE - FIX

## 🚨 THE PROBLEM

**Your Error:** "Error failed to fetch please try again"

**Root Cause:** 
```
HTTP/2 503
x-render-routing: dynamic-hibernate-error-503
```

Your Render **free tier** service hibernates (sleeps) after 15 minutes of inactivity.

When you submit a receipt:
1. Frontend sends request → Backend is asleep (503)
2. Request times out before backend wakes up
3. You see "failed to fetch"

---

## ✅ SOLUTIONS (Choose One)

### **Option 1: Upgrade Render (RECOMMENDED for Production)**

**Go to Render Dashboard:**
1. Open https://dashboard.render.com
2. Find your service: `veritas-engine`
3. Click "Upgrade to Paid"
4. Choose "Starter" plan ($7/month)

**Benefits:**
- ✅ NO hibernation (always awake)
- ✅ Faster response times
- ✅ More RAM (512 MB)
- ✅ Production-ready

**Cost:** $7/month

---

### **Option 2: Keep-Alive Ping (Free Tier Workaround)**

Add a service that pings your backend every 10 minutes to keep it awake.

**Using UptimeRobot (Free):**
1. Go to https://uptimerobot.com
2. Sign up (free)
3. Add monitor:
   - Type: HTTP(s)
   - URL: `https://veritas-engine-zae0.onrender.com/test/status`
   - Interval: 5 minutes
4. Save

**Result:** Server stays awake 24/7 (free!)

---

### **Option 3: Frontend Retry Logic** 

Add retry logic to handle 503 hibernation errors.

**Update your frontend code:**
```javascript
async function uploadReceipt(file, email) {
  const maxRetries = 3;
  const retryDelay = 10000; // 10 seconds
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      // Show status
      if (i === 0) {
        showMessage('Uploading receipt...');
      } else {
        showMessage(`Server waking up... Retry ${i}/${maxRetries}`);
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('email', email);
      
      const response = await fetch(
        'https://veritas-engine-zae0.onrender.com/expenses/scan',
        {
          method: 'POST',
          body: formData,
          signal: AbortSignal.timeout(30000) // 30 second timeout
        }
      );
      
      if (response.status === 503) {
        // Service hibernating, retry
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          continue;
        }
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      showMessage('Receipt processed successfully!');
      return data;
      
    } catch (error) {
      if (i === maxRetries - 1) {
        showMessage('Error: Server took too long to respond. Please try again.');
        throw error;
      }
      // Retry
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
  }
}
```

---

### **Option 4: Manual Wake-Up Page**

Create a simple page that wakes the server before use.

**Add to your app:**
```html
<!-- Add this button to your UI -->
<button onclick="wakeServer()">
  Wake Up Server (Click before uploading)
</button>

<script>
async function wakeServer() {
  const status = document.getElementById('status');
  status.textContent = 'Waking server...';
  
  try {
    await fetch('https://veritas-engine-zae0.onrender.com/test/status');
    
    // Wait 20 seconds for full wake-up
    for (let i = 20; i > 0; i--) {
      status.textContent = `Server waking up... ${i}s`;
      await new Promise(r => setTimeout(r, 1000));
    }
    
    status.textContent = '✅ Server ready! You can now upload.';
  } catch (error) {
    status.textContent = '❌ Error waking server';
  }
}
</script>
```

---

## 🎯 MY RECOMMENDATION

**For Testing/Development:**
→ Use **Option 2** (UptimeRobot keep-alive) - FREE and works perfectly

**For Production/Launch:**
→ Use **Option 1** (Upgrade to $7/month) - Professional and reliable

**Quick Fix (Right Now):**
→ Use **Option 4** (Wake-up button) - Add to your UI immediately

---

## 🔍 HOW TO VERIFY HIBERNATION

**Check if server is awake:**
```bash
curl -I https://veritas-engine-zae0.onrender.com/test/status
```

**If asleep, you'll see:**
```
HTTP/2 503
x-render-routing: dynamic-hibernate-error-503
```

**If awake, you'll see:**
```
HTTP/2 200
```

---

## ⚡ QUICK FIX RIGHT NOW

**From your phone:**

1. Open: https://veritas-engine-zae0.onrender.com/test/status
2. Wait 30 seconds (server wakes up)
3. Now try uploading your receipt
4. Should work!

**Keep it awake:**
- Set a phone reminder to visit that URL every 10 minutes
- Or use UptimeRobot (Option 2)

---

## 📊 RENDER FREE TIER LIMITS

**Hibernation Rules:**
- Sleeps after: 15 minutes of inactivity
- Wake-up time: 10-30 seconds
- Limit: 750 hours/month total (across all services)

**This is why production apps upgrade to paid tier.**

---

## 🔥 BOTTOM LINE

**Your code is fine. Your receipt upload works.**

**The issue:** Render free tier hibernation.

**Quick fix:** Visit /test/status URL to wake it up before uploading

**Real fix:** 
- Free: UptimeRobot (pings every 5 min)
- Paid: Upgrade to $7/month (never sleeps)

---

**Try this RIGHT NOW from your phone:**
1. Open browser
2. Go to: https://veritas-engine-zae0.onrender.com/test/status
3. Wait 30 seconds
4. Go back to your receipt upload page
5. Upload receipt
6. Should work! ✅

---

**Want me to set up UptimeRobot keep-alive for you?** (Keeps server awake 24/7, free)
