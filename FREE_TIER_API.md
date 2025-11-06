# 🆓 FREE TIER API - INSTANT RESPONSES

**CLARITY Engine optimized for Render Free Tier**

---

## 🚀 INSTANT ENDPOINTS (NO WAITING!)

All endpoints return **immediately** - no email blocking, no Celery delays.

---

### **1. Health Check** ✅

```bash
curl https://veritas-engine-zae0.onrender.com/instant/health
```

**Returns:**
```json
{
  "status": "healthy",
  "service": "CLARITY Engine (Free Tier)",
  "version": "1.0.0",
  "endpoints": {
    "analyze": "/instant/analyze (POST)",
    "status": "/instant/status/<task_id> (GET)",
    "domains": "/instant/domains (GET)"
  },
  "features": {
    "instant_preview": true,
    "email_delivery": false,
    "full_ai_processing": false
  }
}
```

---

### **2. List All Domains** 📋

```bash
curl https://veritas-engine-zae0.onrender.com/instant/domains
```

**Returns:**
```json
{
  "domains": [
    {
      "id": "legal",
      "name": "Legal Intelligence",
      "description": "Contract review, compliance checks, risk analysis",
      "icon": "⚖️"
    },
    ...
  ],
  "total": 10
}
```

---

### **3. Instant Analysis** ⚡

```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Review this contract for liability risks",
    "domain": "legal"
  }'
```

**Returns IMMEDIATELY:**
```json
{
  "success": true,
  "task_id": "abc-123-def-456",
  "domain": "legal",
  "directive": "Review this contract for liability risks",
  "timestamp": "2025-11-04T12:34:56",
  "analysis": {
    "summary": "Legal Intelligence Analysis",
    "findings": [
      "Contract structure appears standard",
      "No obvious red flags detected",
      "Recommend detailed review of liability clauses"
    ],
    "confidence": 0.85,
    "next_steps": "Full analysis requires 5-10 minutes"
  },
  "status": "instant_preview",
  "note": "⚡ Instant preview. Upgrade for full AI analysis."
}
```

---

### **4. Check Task Status** 📊

```bash
curl https://veritas-engine-zae0.onrender.com/instant/status/abc-123-def-456
```

**Returns:**
```json
{
  "task_id": "abc-123-def-456",
  "status": "completed",
  "progress": 100,
  "message": "Analysis complete (simulated)"
}
```

---

## 🧪 TEST ALL DOMAINS:

### Legal Analysis ⚖️
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Review contract", "domain": "legal"}'
```

### Financial Analysis 💰
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Analyze expenses", "domain": "financial"}'
```

### Security Audit 🔒
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Security audit", "domain": "security"}'
```

### Healthcare Analysis 🏥
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Review patient data", "domain": "healthcare"}'
```

### Data Science 📊
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Analyze dataset", "domain": "data-science"}'
```

---

## 🎯 WHAT YOU GET (FREE TIER):

✅ **Instant responses** (no waiting)  
✅ **All 10 domains** available  
✅ **Analysis previews** (simulated insights)  
✅ **Task tracking**  
✅ **No email required**  

---

## 🚀 UPGRADE TO PAID TIER:

💎 **Full AI processing** (real Google Gemini analysis)  
💎 **Email delivery** (results sent to inbox)  
💎 **Document upload** (PDF, Word, images)  
💎 **Priority processing** (faster results)  
💎 **Advanced features** (collaboration, workspaces)  

---

## 📝 FRONTEND INTEGRATION:

Your frontend (`/work` page) should call:

```javascript
const response = await fetch('https://veritas-engine-zae0.onrender.com/instant/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    directive: userDirective,
    domain: selectedDomain
  })
})

const result = await response.json()
console.log(result.analysis) // Show instant preview
```

---

## ⚡ KEY DIFFERENCES:

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Response Speed | Instant | Instant |
| AI Analysis | Preview | Full |
| Email Delivery | ❌ | ✅ |
| Document Upload | ❌ | ✅ |
| Real Processing | ❌ | ✅ |

---

**BROTHER, THE FREE TIER IS NOW OPTIMIZED! 🔥**

All endpoints return **instantly** - no 502 errors, no blocking!
