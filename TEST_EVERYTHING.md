# 🧪 TEST EVERYTHING - QUICK START GUIDE

**⚡ 5-MINUTE COMPREHENSIVE TEST**

---

## 🌐 FRONTEND TESTS (Browser)

### **Test 1: Main Landing Page (30 seconds)**
```
URL: https://clarity-engine-auto.vercel.app

✅ Check:
- Page loads with hero section
- 10 domain cards visible with green "LIVE" badges
- API Documentation section present
- Footer lists all 10 domains individually
- Contact: +256 705 885118, nsubugacollin@gmail.com
- Company: "Clarity Pearl"
```

### **Test 2: Command Deck - Legal Analysis (1 minute)**
```
URL: https://clarity-engine-auto.vercel.app/work?domain=legal

✅ Actions:
1. See "Legal Intelligence" selected in sidebar
2. Enter directive: "Review contract for liability clauses"
3. Click "Execute Analysis" button
4. Wait 3-5 seconds
5. See instant analysis preview:
   - Summary: "Legal Intelligence Analysis"
   - Findings: ["Contract structure appears standard", ...]
   - Confidence: 0.85
   - Next steps

✅ Success: Analysis returned in < 5 seconds with structured data
```

### **Test 3: Funding Engine (2 minutes)**
```
URL: https://clarity-engine-auto.vercel.app/funding

✅ Actions:
1. Click "Let's Build Your Package"
2. Answer discovery questions:
   - Project name: "Test Project"
   - Vision: "Test vision"
   - Why: "Test reason"
   - Problem: "Test problem"
   - Solution: "Test solution"
   - Impact: "Test impact"
   - Market: "Test market"
   - Team: "Test team"
   - Traction: (skip)
   - Funding: "$100K"
3. Click "Continue to Document Selection"
4. Click "Select All (25)" documents
5. Enter email: your-email@example.com
6. Click "Generate 25 Documents"
7. See progress bar (0% → 100%, ~60 seconds)
8. See results screen:
   - "Your Funding Package is Ready!"
   - Shows your email address
   - Shows Task ID
   - Blue box says "Free Tier: Preview generated instantly. Email in 5-15 minutes."
   - 3 buttons: Download All, Resend Email, Request Refinement

✅ Success: 
- Email collected
- Task ID generated
- Results screen displays properly
- Buttons are clickable (even if simulated)
```

### **Test 4: Landing Pages (1 minute)**
```
URL 1: https://clarity-engine-auto.vercel.app/compliance
✅ Check: $800K savings, real scenario, pricing section

URL 2: https://clarity-engine-auto.vercel.app/legal
✅ Check: $249K per lawyer, 9 use cases, enterprise pricing

URL 3: https://clarity-engine-auto.vercel.app/financial
✅ Check: $288K per team, CFO case study, 2 pricing tiers
```

### **Test 5: API Documentation (30 seconds)**
```
URL 1: https://clarity-engine-auto.vercel.app/docs
✅ Check: Full API docs, code examples, authentication guide

URL 2: https://clarity-engine-auto.vercel.app/api-keys
✅ Check: Generate API key interface, usage stats, security tips
```

---

## 🖥️ BACKEND TESTS (Terminal/Postman)

### **Test 6: Health Checks**
```bash
# Instant Analysis Health
curl https://veritas-engine-zae0.onrender.com/instant/health
# Expected: {"status":"healthy","service":"CLARITY Engine (Free Tier)","version":"1.0.0"}

# Funding Engine Health
curl https://veritas-engine-zae0.onrender.com/api/funding/health
# Expected: {"status":"healthy","service":"CLARITY Funding Engine","version":"1.0.0"}

# Public API Health
curl https://veritas-engine-zae0.onrender.com/api/health
# Expected: {"status":"healthy","service":"CLARITY Engine API","version":"1.0.0"}
```

### **Test 7: List Domains**
```bash
curl https://veritas-engine-zae0.onrender.com/instant/domains
# Expected: JSON array with 10 domains (legal, financial, security, healthcare, etc.)
```

### **Test 8: Legal Analysis**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Review contract for liability clauses",
    "domain": "legal"
  }'

# Expected:
# {
#   "success": true,
#   "task_id": "uuid",
#   "domain": "legal",
#   "directive": "Review contract for liability clauses",
#   "files_received": 0,
#   "timestamp": "2025-11-05T...",
#   "analysis": {
#     "summary": "Legal Intelligence Analysis",
#     "findings": ["Contract structure appears standard", "No obvious red flags detected"],
#     "confidence": 0.85,
#     "next_steps": "Full analysis requires 5-15 minutes"
#   },
#   "status": "instant_preview",
#   "note": "⚡ Instant preview generated. Upgrade for full AI analysis + email delivery."
# }
```

### **Test 9: Financial Analysis**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Analyze financial statements for anomalies",
    "domain": "financial"
  }'

# Expected: Similar structure with financial-specific analysis preview
```

### **Test 10: Funding Package Generation**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/api/funding/generate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "discovery_answers": {
      "project_name": "Test Project",
      "vision": "Test vision",
      "problem": "Test problem",
      "solution": "Test solution",
      "impact": "Test impact",
      "market": "Test market",
      "team": "Test team",
      "funding_need": "$100K"
    },
    "config": {
      "fundingLevel": "seed",
      "targetAudience": "investors",
      "selectedDocuments": ["vision", "pitch_deck", "business_plan"]
    }
  }'

# Expected:
# {
#   "success": true,
#   "task_id": "uuid",
#   "email": "test@example.com",
#   "documents_count": 3,
#   "estimated_time_minutes": 15,
#   "message": "Your funding package is being generated! You will receive an email at test@example.com when ready.",
#   "note": "⚡ Free tier: Simulated generation. Upgrade to Enterprise for real AI-powered document generation.",
#   "status": "queued"
# }
```

---

## ✅ SUCCESS CRITERIA

### **All Tests Pass If:**
1. ✅ All frontend pages load without 404 errors
2. ✅ Command Deck submits analysis and returns results
3. ✅ Funding Engine collects email and generates Task ID
4. ✅ Landing pages display pain points and ROI correctly
5. ✅ All backend health checks return 200 OK
6. ✅ Analysis endpoints return structured JSON with "success": true
7. ✅ Funding endpoint accepts requests and returns Task ID

---

## 🐛 COMMON ISSUES & FIXES

### **Issue: 404 on Frontend Pages**
- **Cause:** Vercel deployment not complete
- **Fix:** Wait 2-3 minutes for Vercel to finish deploying
- **Check:** Visit https://vercel.com/your-project/deployments

### **Issue: Backend 502 Error**
- **Cause:** Render service sleeping (free tier)
- **Fix:** First request wakes it up (wait 30 seconds, retry)
- **Check:** Visit https://veritas-engine-zae0.onrender.com/instant/health

### **Issue: Analysis Returns Error**
- **Cause:** Invalid domain or missing directive
- **Fix:** Ensure domain is one of: legal, financial, security, healthcare, data-science, education, proposals, ngo, data-entry, expenses
- **Fix:** Ensure directive is a non-empty string

### **Issue: Funding Engine Doesn't Submit**
- **Cause:** Email validation failed
- **Fix:** Enter valid email with @ and . (e.g., test@example.com)
- **Fix:** Select at least 1 document before clicking Generate

---

## 📊 EXPECTED PERFORMANCE

| Test | Expected Time | Status |
|------|---------------|--------|
| Frontend Page Load | < 2 seconds | ✅ |
| Backend Health Check | < 1 second | ✅ |
| Analysis Submission | < 5 seconds | ✅ |
| Funding Submission | < 5 seconds | ✅ |
| Frontend Build | < 3 minutes | ✅ |
| Backend Wake-Up (first request) | 30-60 seconds | ⚠️ (Free tier) |

---

## 🎯 NEXT STEPS AFTER TESTING

### **If All Tests Pass:**
1. ✅ Platform is production-ready
2. ✅ Share links with potential customers
3. ✅ Start collecting feedback
4. ✅ Move to email activation phase

### **If Some Tests Fail:**
1. 📝 Document exact error messages
2. 📸 Screenshot the issue
3. 💬 Share with development team (nsubugacollin@gmail.com)
4. 🔧 Wait for fix + retest

---

## 📞 SUPPORT

**Need Help?**
- **Email:** nsubugacollin@gmail.com
- **Phone:** +256 705 885118
- **GitHub:** https://github.com/colmeta/compliancecopilot2

---

**🚀 READY TO TEST? LET'S GO!**

**Start with Test 1 (Landing Page) and work your way down.**  
**Each test should take < 2 minutes.**  
**Total testing time: 10-15 minutes.**

---

*Last Updated: November 5, 2025*  
*Platform: CLARITY Engine by Clarity Pearl*
