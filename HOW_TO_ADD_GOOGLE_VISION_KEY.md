# 🔑 How to Add Your Google Cloud Vision API Key

## You Already Have the Key! Now Let's Configure It

---

## 🎯 QUICK GUIDE: Add OCR Key to Render (2 Minutes)

### **Step 1: Locate Your API Key**

You mentioned you got the Google Cloud Vision API key. It should look like one of these:

**Option A: API Key (Simple)**
```
AIzaSyD...your-key-here
```

**Option B: Service Account JSON (Advanced)**
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  ...
}
```

---

## 🚀 ADD TO RENDER (Choose Your Method)

### **Method 1: If You Have an API Key (Recommended)**

1. **Go to Render:**
   - URL: https://dashboard.render.com
   - Select your CLARITY backend service

2. **Add Environment Variable:**
   - Click "Environment" tab on the left
   - Click "Add Environment Variable"
   - **Key:** `GOOGLE_VISION_API_KEY`
   - **Value:** (Paste your API key, e.g., `AIzaSyD...`)
   - Click "Save Changes"

3. **Wait for Redeploy:**
   - Render will automatically redeploy (2-3 minutes)
   - Watch the logs for "Build succeeded"

4. **Test It:**
   ```bash
   curl https://your-backend.onrender.com/ocr/status
   ```
   
   Expected response:
   ```json
   {
     "success": true,
     "engines_available": {
       "tesseract": true,
       "google_vision": true
     }
   }
   ```

---

### **Method 2: If You Have a Service Account JSON File**

1. **Option A: Upload File to Render (if Render supports file upload)**
   - Upload the JSON file to your Render service
   - Add environment variable:
     ```
     GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
     ```

2. **Option B: Use JSON as Environment Variable (Easier)**
   - Open your JSON file
   - Copy the ENTIRE contents
   - Go to Render → Environment
   - Add variable:
     - **Key:** `GOOGLE_APPLICATION_CREDENTIALS_JSON`
     - **Value:** (Paste entire JSON content)
   - Click "Save Changes"

3. **Update Your Code (if needed):**
   
   Your backend should automatically handle this, but verify in `config.py`:
   ```python
   GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')
   # OR
   GOOGLE_APPLICATION_CREDENTIALS_JSON = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
   ```

---

## 🧪 VERIFY IT'S WORKING

### Test 1: Check OCR Status
```bash
curl https://your-backend.onrender.com/ocr/status
```

**Expected Response:**
```json
{
  "success": true,
  "status": {
    "engines_available": {
      "tesseract": true,
      "google_vision": true
    },
    "google_vision_usage": {
      "monthly_usage": 0,
      "free_limit": 1000,
      "remaining_free": 1000
    }
  }
}
```

---

### Test 2: Upload a Test Image (If you have one)

Create a simple test image or use any receipt/document:

```bash
curl -X POST https://your-backend.onrender.com/ocr/extract \
  -F "file=@your-receipt.jpg" \
  -F "use_premium=true"
```

**Expected Response:**
```json
{
  "success": true,
  "text": "Extracted text from your image...",
  "confidence": 96.5,
  "engine": "google_vision",
  "cost": 0.0,
  "free_tier": true
}
```

---

### Test 3: Full Integration Test

Test OCR + AI Analysis together:

```bash
# 1. Upload image and extract text (OCR)
# 2. Then analyze with Legal Intelligence
curl -X POST https://your-backend.onrender.com/real/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "legal",
    "directive": "Extract and analyze contract terms",
    "document_content": "Scanned contract text here...",
    "use_outstanding": true
  }'
```

---

## 🔐 SECURITY BEST PRACTICES

### ✅ DO:
- Store key as environment variable (never in code)
- Use `.env` for local development
- Add `.env` to `.gitignore`
- Rotate keys every 90 days
- Set budget alerts on Google Cloud

### ❌ DON'T:
- Commit keys to git
- Share keys publicly
- Hardcode keys in source files
- Leave unused keys active

---

## 💰 COST MANAGEMENT

### Free Tier (What You Get)
- **1,000 requests/month FREE**
- Resets monthly
- No credit card charge if you stay under 1,000

### After Free Tier
- **$1.50 per 1,000 requests**
- Very affordable!

### Example Costs:
| Usage | Monthly Cost |
|-------|--------------|
| 500 documents | $0 (FREE) |
| 1,000 documents | $0 (FREE) |
| 5,000 documents | $6.00 |
| 10,000 documents | $13.50 |
| 100,000 documents | $148.50 |

### Set Budget Alerts:
1. Go to: https://console.cloud.google.com/billing/budgets
2. Create budget: $10, $50, $100
3. Get email alerts before charges hit

---

## 🛠️ TROUBLESHOOTING

### Issue: "google_vision not available"

**Solution:**
```bash
# Check if key is set:
curl https://your-backend.onrender.com/health

# Verify key in Render:
# 1. Go to Render dashboard
# 2. Click Environment tab
# 3. Confirm GOOGLE_VISION_API_KEY is there
# 4. Trigger manual redeploy if needed
```

---

### Issue: "Billing not enabled"

**Solution:**
```bash
# Go to: https://console.cloud.google.com/billing
# 1. Enable billing (add credit card)
# 2. Don't worry - you won't be charged for first 1,000 requests!
# 3. Set budget alerts to be safe
```

---

### Issue: "API not enabled"

**Solution:**
```bash
# Go to: https://console.cloud.google.com/apis/library/vision.googleapis.com
# Click "Enable"
# Wait 1-2 minutes for activation
```

---

### Issue: "403 Forbidden"

**Solution:**
```bash
# Your API key may not have Vision API permissions
# 1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
# 2. Find your service account
# 3. Add role: "Cloud Vision API User"
# 4. Save
```

---

## 📋 COMPLETE RENDER ENVIRONMENT VARIABLES

Here's your complete environment setup for Render:

```bash
# CRITICAL (Must have)
GOOGLE_API_KEY=your_gemini_key_here
GOOGLE_VISION_API_KEY=your_google_cloud_vision_key_here
FLASK_SECRET_KEY=your_secure_random_key_min_32_chars

# HIGHLY RECOMMENDED
GROQ_API_KEY=your_groq_key_here
ENABLE_OUTSTANDING_MODE=true
ENABLE_OCR_PROCESSING=true
ENABLE_MODEL_ROUTING=true
ENABLE_RESPONSE_CACHE=true
ENABLE_AI_OPTIMIZATION=true

# OPTIONAL (If you have OpenAI)
OPENAI_API_KEY=your_openai_key_here

# FEATURE FLAGS
DEFAULT_TIER=free
ENABLE_AUDIT_LOGGING=true
ENABLE_PII_DETECTION=true
```

---

## ✅ VERIFICATION CHECKLIST

After adding the key, verify:

- [ ] Environment variable added in Render
- [ ] Render auto-deployed (check logs)
- [ ] Health check shows OCR available
- [ ] Test OCR extraction works
- [ ] Google Cloud billing enabled (if using premium)
- [ ] Budget alerts set
- [ ] Free tier confirmed (1,000/month)

---

## 🎯 YOU'RE DONE!

Your CLARITY Engine now has:
- ✅ Google Cloud Vision OCR (premium accuracy)
- ✅ Tesseract OCR (free fallback)
- ✅ Smart routing (cost optimization)
- ✅ 1,000 free requests/month
- ✅ Presidential-grade document processing

**Test it now:**
```bash
bash /workspace/PRESIDENTIAL_TEST_SUITE.sh
```

---

## 📞 NEED HELP?

**Developer:** Nsubuga Collin  
**Email:** nsubugacollin@gmail.com  
**Phone:** +256 705 885 118

---

**🏛️ Your OCR system is now presidential-grade! Launch and dominate! 🚀**
