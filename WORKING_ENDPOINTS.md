# ✅ WORKING ENDPOINTS (CONFIRMED)

**Backend:** https://veritas-engine-zae0.onrender.com

---

## 🟢 CONFIRMED WORKING:

### 1. **Instant Domains** ✅
```bash
curl https://veritas-engine-zae0.onrender.com/instant/domains
```
**Returns:** All 10 domains with descriptions

### 2. **Instant Health** ✅  
```bash
curl https://veritas-engine-zae0.onrender.com/instant/health
```
**Returns:** Backend status, version, features

### 3. **Instant Analyze** ✅
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{"directive": "Test", "domain": "legal"}'
```
**Returns:** Instant analysis preview with findings

### 4. **Quick Test** ✅
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/quick/test \
  -H "Content-Type: application/json" \
  -d '{"directive": "Test", "domain": "financial"}'
```
**Returns:** Quick analysis preview

### 5. **Quick Domains** ✅
```bash
curl https://veritas-engine-zae0.onrender.com/quick/domains
```
**Returns:** All 10 domains

### 6. **Test Status** ✅
```bash
curl https://veritas-engine-zae0.onrender.com/test/status
```
**Returns:** Backend environment configuration

---

## 🔴 NOT YET WORKING:

### `/api/domains` ❌
```bash
curl https://veritas-engine-zae0.onrender.com/api/domains
```
**Returns:** `{"error":"Not found"}`

**Why:** Blueprint registration issue (being fixed)

---

## 💡 WORKAROUND FOR FRONTEND:

Use the **`/instant/*`** endpoints instead of `/api/*`:

```javascript
// Instead of /api/domains
const response = await fetch('https://veritas-engine-zae0.onrender.com/instant/domains')

// Instead of /api/analyze  
const response = await fetch('https://veritas-engine-zae0.onrender.com/instant/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ directive, domain })
})
```

---

## 🎯 FRONTEND INTEGRATION:

### Example: Connect Command Deck

```javascript
// frontend/app/work/page.tsx

const BACKEND_URL = 'https://veritas-engine-zae0.onrender.com'

// Fetch domains
const fetchDomains = async () => {
  const res = await fetch(`${BACKEND_URL}/instant/domains`)
  const data = await res.json()
  return data.domains
}

// Submit analysis
const submitAnalysis = async (directive, domain) => {
  const res = await fetch(`${BACKEND_URL}/instant/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ directive, domain })
  })
  
  const result = await res.json()
  return result.analysis  // Contains findings, confidence, etc.
}
```

---

## 📊 RESPONSE FORMAT:

### Domain List Response:
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

### Analysis Response:
```json
{
  "success": true,
  "task_id": "uuid-here",
  "domain": "legal",
  "directive": "Your task",
  "analysis": {
    "summary": "Legal Intelligence Analysis",
    "findings": [
      "Finding 1",
      "Finding 2",
      "Finding 3"
    ],
    "confidence": 0.85,
    "next_steps": "Full analysis requires 5-10 minutes"
  },
  "status": "instant_preview"
}
```

---

**BROTHER, USE `/instant/*` ENDPOINTS - THEY ALL WORK! 🔥**
