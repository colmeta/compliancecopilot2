# 🔍 OCR SETUP GUIDE - Extract Text from Images
## FREE Tesseract + Premium Google Vision

---

## 💰 PRICING (CLEAR ANSWER TO YOUR QUESTION)

### **Google Cloud Vision OCR:**

✅ **FREE TIER: 1,000 pages/month** 🎉  
💳 **Requires credit card** (but won't charge if you stay in free tier)  
💰 **After free tier: $1.50 per 1,000 pages** (very cheap!)

**Example Costs:**
- **1,000 scanned receipts/month = FREE** ✅
- **10,000 receipts/month = $13.50/month** 💵
- **100,000 receipts/month = $148.50/month** 💵

### **Tesseract OCR:**

✅ **100% FREE FOREVER** (no credit card needed!)  
✅ **Runs on your server** (no API calls)  
❌ **Lower accuracy** (80-90% vs Google's 95-99%)  
❌ **Struggles with handwriting**

---

## 🎯 MY RECOMMENDATION

**Use BOTH with smart fallback:**

```python
# 1. Try FREE Tesseract first
text = tesseract_ocr(image)  # FREE

# 2. If low confidence, use Google Vision
if confidence < 85% and monthly_usage < 1000:
    text = google_vision_ocr(image)  # FREE up to 1,000/month

# 3. This way you minimize costs!
```

**Result:**
- Most documents use FREE Tesseract (80-90% accuracy)
- Only difficult documents use Google Vision (95-99% accuracy)
- Stay within 1,000 Google Vision pages/month = **100% FREE!**

---

## 📦 OPTION 1: FREE TESSERACT (Recommended to Start)

### **Installation on Render/Ubuntu:**

Add to your `build.sh` or Dockerfile:

```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y libtesseract-dev
```

### **Python Dependencies (Already in requirements.txt):**

```bash
pytesseract>=0.3.10
pdf2image>=1.16.3
Pillow>=10.0.0
```

### **Test Tesseract:**

```bash
curl -X POST https://your-backend.onrender.com/ocr/extract \
  -F "file=@receipt.jpg" \
  -F "use_premium=false" \
  -F "language=eng"
```

**Expected Response:**

```json
{
  "success": true,
  "text": "Extracted text from your receipt...",
  "confidence": 87.5,
  "engine": "tesseract",
  "cost": 0.0,
  "word_count": 125,
  "processing_time": 1.2,
  "free_tier": true
}
```

---

## 📦 OPTION 2: GOOGLE CLOUD VISION (Premium, 1,000 FREE/month)

### **Step 1: Get Google Cloud Account**

1. Go to: https://console.cloud.google.com
2. **Create account** (requires credit card ⚠️)
3. **Enable billing** (but won't charge for first 1,000/month!)

### **Step 2: Enable Vision API**

1. Go to: https://console.cloud.google.com/apis/library/vision.googleapis.com
2. Click **"Enable"**
3. Wait 1-2 minutes for activation

### **Step 3: Create Service Account**

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **"Create Service Account"**
3. Name: `clarity-ocr-service`
4. Role: **"Cloud Vision API User"**
5. Click **"Create Key"** → JSON
6. Download the JSON file

### **Step 4: Add to Render**

1. Open the downloaded JSON file
2. Copy the ENTIRE contents
3. Go to Render → Your service → Environment
4. Add new variable:
   - **Name**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: (paste the entire JSON content)

**OR** upload the file to Render and set path:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### **Step 5: Set Budget Alerts (Prevent Surprise Charges!)**

1. Go to: https://console.cloud.google.com/billing/budgets
2. Click **"Create Budget"**
3. Set alerts:
   - Alert at $10
   - Alert at $50  
   - Alert at $100
4. Get email notifications before charges hit!

### **Step 6: Test Google Vision:**

```bash
curl -X POST https://your-backend.onrender.com/ocr/extract \
  -F "file=@handwritten_note.jpg" \
  -F "use_premium=true" \
  -F "language=eng"
```

**Expected Response:**

```json
{
  "success": true,
  "text": "Extracted handwritten text...",
  "confidence": 96.8,
  "engine": "google_vision",
  "cost": 0.0,
  "word_count": 245,
  "processing_time": 0.8,
  "free_tier": true
}
```

---

## 🚀 USAGE EXAMPLES

### **Example 1: Scan Receipt (Your Sister's Law Firm)**

```bash
curl -X POST https://your-backend.onrender.com/ocr/extract \
  -F "file=@receipt.jpg"
```

**Response:**

```json
{
  "success": true,
  "text": "ABC Store\n123 Main St\nDate: 11/06/2025\nItem 1: $19.99\nItem 2: $34.50\nTotal: $54.49",
  "confidence": 89.2,
  "engine": "tesseract",
  "cost": 0.0,
  "free_tier": true
}
```

### **Example 2: Scan Legal Document (Complex Layout)**

```bash
curl -X POST https://your-backend.onrender.com/ocr/extract \
  -F "file=@legal_contract.pdf" \
  -F "use_premium=true"
```

**Response:**

```json
{
  "success": true,
  "text": "[Full contract text extracted...]",
  "confidence": 97.3,
  "engine": "google_vision",
  "cost": 0.0,
  "pages_processed": 5,
  "free_tier": true
}
```

### **Example 3: Check Usage Status**

```bash
curl https://your-backend.onrender.com/ocr/status
```

**Response:**

```json
{
  "success": true,
  "status": {
    "engines_available": {
      "tesseract": true,
      "google_vision": true
    },
    "google_vision_usage": {
      "monthly_usage": 245,
      "free_limit": 1000,
      "remaining_free": 755,
      "cost_after_free_tier": "$1.50 per 1,000 pages"
    },
    "recommendations": [
      "✅ Using FREE Tesseract OCR (80-90% accuracy)",
      "✅ Google Vision within free tier"
    ]
  },
  "pricing": {
    "tesseract": {
      "cost": "$0 (FREE forever)",
      "accuracy": "80-90%"
    },
    "google_vision": {
      "free_tier": "1,000 pages/month",
      "paid_tier": "$1.50 per 1,000 pages",
      "accuracy": "95-99%"
    }
  }
}
```

---

## 🎯 INTEGRATION WITH CLARITY DOMAINS

### **Legal Intelligence:**

```bash
# User uploads scanned legal document
POST /ocr/extract (file=legal_doc.pdf)
  ↓
# Extract text with OCR
GET text from OCR
  ↓
# Analyze with Legal Intelligence
POST /real/analyze 
  domain=legal, 
  directive="Review for risks", 
  document_content=extracted_text
  ↓
# Return legal analysis
{
  "findings": [...],
  "risks": [...],
  "recommendations": [...]
}
```

### **Financial Intelligence (Expense Management):**

```bash
# User uploads receipt photo
POST /ocr/extract (file=receipt.jpg)
  ↓
# Extract receipt data
{
  "text": "Store X, Total: $123.45, Date: 11/06/2025"
}
  ↓
# Categorize expense
POST /real/analyze
  domain=financial,
  directive="Categorize expense and extract details"
  ↓
# Return categorized expense
{
  "merchant": "Store X",
  "amount": 123.45,
  "category": "Office Supplies",
  "date": "2025-11-06"
}
```

---

## 💡 COST OPTIMIZATION STRATEGIES

### **Strategy 1: Free-First Fallback**

```python
# Default configuration (in OCR engine)
use_premium = False
auto_fallback = True

# Result:
# - 90% of documents: Tesseract (FREE)
# - 10% of documents: Google Vision (HIGH ACCURACY)
# - Total cost: $0-$5/month for most users
```

### **Strategy 2: User Tier-Based**

```python
if user.tier == 'free':
    use_premium = False  # Tesseract only
elif user.tier == 'pro':
    use_premium = True  # Google Vision (user pays)
    monthly_limit = 100  # Limit to control costs
elif user.tier == 'enterprise':
    use_premium = True  # Google Vision unlimited
    monthly_limit = 10000
```

### **Strategy 3: Confidence Threshold**

```python
# Try Tesseract first
result = tesseract_ocr(image)

# Only use Google if Tesseract fails
if result.confidence < 80:
    result = google_vision_ocr(image)  # Better accuracy
```

---

## 🛡️ PREVENT SURPRISE CHARGES

### **1. Set Budget Alerts (Google Cloud Console)**

- Alert at $10, $50, $100
- Get email before charges hit
- Can set hard limits to stop API calls

### **2. Track Usage in Code**

```python
# Built into OCR engine
if monthly_google_usage >= free_limit:
    # Either:
    # A) Fallback to Tesseract
    # B) Show upgrade message to user
    # C) Charge user per scan
```

### **3. Monthly Usage Reports**

```bash
GET /ocr/status

{
  "google_vision_usage": {
    "monthly_usage": 245,
    "free_limit": 1000,
    "remaining_free": 755
  }
}
```

---

## 📊 COMPARISON: TESSERACT vs GOOGLE VISION

| Feature | Tesseract (FREE) | Google Vision (Premium) |
|---------|------------------|-------------------------|
| **Cost** | $0 forever | $0 (first 1,000/month), then $1.50/1,000 |
| **Credit Card** | Not needed | Required (but not charged if < 1,000) |
| **Accuracy** | 80-90% | 95-99% |
| **Printed Text** | ✅ Excellent | ✅ Excellent |
| **Handwriting** | ❌ Poor | ✅ Excellent |
| **Complex Layouts** | ⚠️ OK | ✅ Excellent |
| **Multi-Language** | ✅ Good | ✅ Excellent |
| **Speed** | Fast (local) | Fast (API) |
| **Setup** | Easy | Moderate (needs Google account) |

---

## ✅ TESTING CHECKLIST

- [ ] Install Tesseract on server
- [ ] Test with simple receipt (Tesseract)
- [ ] Create Google Cloud account (if using premium)
- [ ] Enable Vision API
- [ ] Create service account + download JSON
- [ ] Add JSON to Render environment
- [ ] Set budget alerts ($10, $50, $100)
- [ ] Test with handwritten document (Google Vision)
- [ ] Check usage status
- [ ] Verify costs are $0 (within free tier)

---

## 🎉 READY!

**Your OCR system is now complete with:**

✅ **FREE Tesseract** (80-90% accuracy, $0 forever)  
✅ **Premium Google Vision** (95-99% accuracy, 1,000 FREE/month)  
✅ **Smart fallback** (minimize costs)  
✅ **Usage tracking** (prevent surprise charges)  
✅ **Multi-format support** (JPG, PNG, PDF, TIFF)  
✅ **API endpoints ready** (`/ocr/extract`, `/ocr/status`)

**Perfect for your sister's law firm! 📄⚖️**

---

**Contact:** nsubugacollin@gmail.com | +256 705 885 118  
**Company:** Clarity Pearl | CLARITY Engine
