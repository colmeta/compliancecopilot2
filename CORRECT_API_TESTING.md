# ✅ CORRECT API TESTING GUIDE

**Your Application:** https://veritas-engine-zae0.onrender.com

## 🚨 THE ISSUE

You're accessing URLs like this (❌ WRONG):
```
https://veritas-engine-zae0.onrender.com/test/analyze%20/%20-H%20%22Content-Type:%20application/json%22%20/%20-d%20'%7B%22directive%22:%22Test%22,%22domain%22:%22legal%22%7D'
```

This encodes the **entire curl command** as the URL path. That's why you get 404 errors.

---

## ✅ CORRECT USAGE

### **Test Endpoints** (Simple, No AI)

#### 1. Test Analyze (POST)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive":"Test contract review","domain":"legal"}'
```

#### 2. Test Status (GET)
```bash
curl https://veritas-engine-zae0.onrender.com/test/status
```

#### 3. Test Domains (GET)
```bash
curl https://veritas-engine-zae0.onrender.com/test/domains
```

---

### **Real AI Endpoints** (Google Gemini)

#### 1. Real Analyze (POST)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/real/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Review for risks",
    "domain": "legal",
    "document_content": "Sample contract: Company A agrees to provide services for $10,000. Neither party liable for consequential damages."
  }'
```

#### 2. Real Health (GET) ✅ Already Working
```bash
curl https://veritas-engine-zae0.onrender.com/real/health
```

#### 3. Real Domains (GET) ✅ Already Working
```bash
curl https://veritas-engine-zae0.onrender.com/real/domains
```

---

### **Instant Endpoints** (Free Tier)

#### 1. Instant Analyze (POST)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive":"Analyze this contract","domain":"legal"}'
```

#### 2. Instant Health (GET)
```bash
curl https://veritas-engine-zae0.onrender.com/instant/health
```

#### 3. Instant Domains (GET)
```bash
curl https://veritas-engine-zae0.onrender.com/instant/domains
```

---

### **Quick Test Endpoints**

#### 1. Quick Test (POST)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/quick/test \
  -H "Content-Type: application/json" \
  -d '{"directive":"Test","domain":"financial"}'
```

#### 2. Quick Domains (GET)
```bash
curl https://veritas-engine-zae0.onrender.com/quick/domains
```

---

## 🧪 TESTING FROM BROWSER

### Using JavaScript Fetch (Browser Console)

#### Test Real AI Analyze:
```javascript
fetch('https://veritas-engine-zae0.onrender.com/real/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    directive: 'Review for risks',
    domain: 'legal',
    document_content: 'Sample contract: Company A agrees to provide services for $10,000. Neither party liable for consequential damages.'
  })
})
.then(r => r.json())
.then(data => console.log('✅ Result:', data))
.catch(err => console.error('❌ Error:', err))
```

#### Test Simple Analyze:
```javascript
fetch('https://veritas-engine-zae0.onrender.com/test/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    directive: 'Test contract review',
    domain: 'legal'
  })
})
.then(r => r.json())
.then(data => console.log('✅ Result:', data))
.catch(err => console.error('❌ Error:', err))
```

---

## 🎯 POSTMAN / INSOMNIA SETUP

### Request Configuration:

**Method:** `POST`  
**URL:** `https://veritas-engine-zae0.onrender.com/real/analyze`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "directive": "Review this contract for legal risks",
  "domain": "legal",
  "document_content": "This is a sample contract between Company A and Company B. Company A will provide consulting services for $50,000. Payment due within 30 days. Neither party shall be liable for consequential damages."
}
```

---

## 📊 ALL AVAILABLE POST ENDPOINTS

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/test/analyze` | POST | Simple test (no AI) | ❌ No |
| `/instant/analyze` | POST | Instant preview | ❌ No |
| `/quick/test` | POST | Quick test | ❌ No |
| `/real/analyze` | POST | **Real AI (Gemini)** | ❌ No |
| `/api/analyze` | POST | Full analysis | ✅ Yes |
| `/funding/analyze` | POST | Funding analysis | ❌ No |

---

## 🔥 QUICK COPY-PASTE TESTS

### Test 1: Simple (No AI)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/analyze -H "Content-Type: application/json" -d '{"directive":"Test","domain":"legal"}'
```

### Test 2: Real AI (Gemini)
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/real/analyze -H "Content-Type: application/json" -d '{"directive":"Review for risks","domain":"legal","document_content":"Sample contract text here"}'
```

### Test 3: Instant Preview
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze -H "Content-Type: application/json" -d '{"directive":"Analyze","domain":"legal"}'
```

---

## 🐛 TROUBLESHOOTING

### ❌ Getting 404 Errors?

**Check:**
1. Are you using the correct URL format?
   - ✅ `https://veritas-engine-zae0.onrender.com/test/analyze`
   - ❌ `https://veritas-engine-zae0.onrender.com/test/analyze / -H ...`

2. Are you using the correct HTTP method?
   - Most analyze endpoints require `POST` not `GET`

3. Are you setting the Content-Type header?
   - Required: `Content-Type: application/json`

### ❌ Getting Empty Responses?

**Check:**
1. Are you sending a request body for POST requests?
2. Is the JSON properly formatted?
3. Are required fields included? (`directive`, `domain`)

---

## ✅ EXPECTED RESPONSES

### Test Analyze Response:
```json
{
  "success": true,
  "domain": "legal",
  "directive": "Test contract review",
  "analysis": {
    "summary": "Legal Intelligence Analysis",
    "findings": ["Finding 1", "Finding 2", "Finding 3"],
    "confidence": 0.75
  }
}
```

### Real AI Analyze Response:
```json
{
  "success": true,
  "analysis": {
    "domain": "legal",
    "findings": ["AI-generated insights..."],
    "confidence": 0.92,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "model": "gemini-1.5-flash",
  "processing_time": 2.3
}
```

---

## 🚀 YOUR APPLICATION IS WORKING!

The logs show all routes registered successfully:
- ✅ Simple test routes
- ✅ Quick test routes  
- ✅ Instant routes
- ✅ Real AI routes (Gemini)
- ✅ Funding document generator
- ✅ OCR service
- ✅ Expense management
- ✅ All 10 domains active

**The issue is just URL formatting in your test requests!**

Use the curl commands above, and everything will work. 🔥
