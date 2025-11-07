# 🚨 QUICK FIX GUIDE - "Not Found" Error

## ❌ PROBLEM: Getting `{"error":"Not found"}` or `{"detail":"Not Found"}`

### 🔍 **ROOT CAUSE:**

Your Render backend hasn't redeployed with the new code yet!

---

## ✅ **SOLUTION (2 minutes):**

### **Step 1: Trigger Render Redeploy**

Go to: https://dashboard.render.com

1. Find your backend service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. **IMPORTANT: Uncheck "Use existing build cache"** ✅
4. Wait 5-10 minutes for deployment

### **Step 2: Verify New Code is Live**

```bash
# Check if V2 endpoints exist
curl https://your-backend.onrender.com/v2/funding/health
```

**Should return:**
```json
{
  "success": true,
  "status": "fully_operational",
  "version": "2.0",
  "quality_standard": "Presidential / Fortune 50"
}
```

**If you get "Not Found"** → Render hasn't redeployed yet, wait longer

---

## 📧 **EMAIL CONFIGURATION (CORRECT WAY):**

### **⚠️ IMPORTANT: Where to Put Email Address**

**WRONG ❌:**
```bash
# Don't put YOUR email in the test command placeholder!
curl -X POST ... \
  -d '{"email": "your_gmail@gmail.com"}'  # This is WHERE to SEND results
```

**CORRECT ✅:**
```bash
# Put YOUR email where you want to RECEIVE results
curl -X POST https://your-backend.onrender.com/v2/funding/generate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_EMAIL@gmail.com",  # ← Where YOU want to receive the package
    "discovery_answers": { ... }
  }'
```

### **Email in Environment Variables (Render):**

**CORRECT Setup:**

```bash
# In Render Environment Variables:
MAIL_USERNAME=your_gmail@gmail.com        # ← Gmail you created app password for
MAIL_PASSWORD=abcd efgh ijkl mnop         # ← 16-character app password
ENABLE_EMAIL_DELIVERY=true
```

**Explanation:**
- `MAIL_USERNAME` = Your Gmail account that SENDS emails
- `email` in API request = Recipient who RECEIVES the package
- These are DIFFERENT emails! (can be same, but conceptually different)

---

## 🧪 **CORRECT TEST COMMAND:**

### **After Render redeploys, use this:**

```bash
curl -X POST https://your-backend.onrender.com/v2/funding/health
```

**Expected:** `"status": "fully_operational"`

**Then test generation:**

```bash
curl -X POST https://your-backend.onrender.com/v2/funding/generate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_PERSONAL_EMAIL@gmail.com",
    "discovery_answers": {
      "company_name": "TestCo",
      "industry": "SaaS",
      "problem": "Slow data analysis",
      "solution": "AI-powered platform",
      "traction": "$50K MRR, 20 customers",
      "team": "Ex-Google engineers",
      "funding_goal": "$2M seed"
    },
    "config": {
      "fundingLevel": "seed",
      "selectedDocuments": ["one_pager", "vision"],
      "formats": ["pdf", "word"],
      "delivery": "email"
    }
  }'
```

Replace `YOUR_PERSONAL_EMAIL@gmail.com` with where YOU want to receive the funding package.

---

## 🔍 **DEBUGGING CHECKLIST:**

### **If still "Not Found":**

1. ✅ Check Render deployed successfully
   - Go to Render dashboard
   - Check "Logs" tab
   - Look for: `"✅ Complete funding workflow V2 registered"`

2. ✅ Check you're using correct URL
   - NOT: `clarity-engine-auto.vercel.app` (frontend)
   - YES: `your-backend-name.onrender.com` (backend)

3. ✅ Check endpoint path
   - NOT: `/funding/generate`
   - YES: `/v2/funding/generate`

4. ✅ Check Render environment variables
   ```bash
   GOOGLE_API_KEY=your_key              # ✅ Set
   MAIL_USERNAME=your_gmail@gmail.com   # ✅ Set
   MAIL_PASSWORD=your_app_password      # ✅ Set (16 chars)
   ENABLE_EMAIL_DELIVERY=true           # ✅ Set
   ```

---

## 📊 **FIND YOUR RENDER URL:**

**Don't know your backend URL?**

```bash
# In your terminal:
git remote -v

# Output shows your GitHub repo
# Then go to Render dashboard and find the .onrender.com URL
```

**OR:**

Go to: https://dashboard.render.com
- Click your service
- Look for: `https://your-service-name.onrender.com`

---

## 🚀 **ONCE FIXED, TEST THESE:**

### **1. V2 Funding Engine:**
```bash
curl https://YOUR_BACKEND.onrender.com/v2/funding/health
```

### **2. OCR System:**
```bash
curl https://YOUR_BACKEND.onrender.com/ocr/health
```

### **3. Real AI Analysis:**
```bash
curl https://YOUR_BACKEND.onrender.com/real/health
```

**All should return `"success": true`**

---

## 💡 **TL;DR:**

1. **Render needs to redeploy** (5-10 min) ← MOST COMMON ISSUE
2. **Use `/v2/funding/health` endpoint** (not old `/real/funding/`)
3. **Email in request = where to SEND results** (your personal email)
4. **Email in env vars = what account SENDS emails** (Gmail with app password)

**Wait for Render to finish deploying, then test again!** ⏰
