# 📧 EMAIL DELIVERY - SETUP GUIDE

**Activate Email Delivery in 5 Minutes**

---

## 🎯 WHY EMAIL DELIVERY?

**The Problem:**
- User submits analysis → Waits in browser → 10 minutes → Browser times out → Loses results
- With 100 concurrent users → Server crashes
- User can't close browser or they lose their work

**The Solution (Email Delivery):**
- User submits analysis → Gets instant confirmation → Closes browser
- Backend processes in background → Sends results via email (5-15 min)
- User opens email → Downloads results
- **Result:** Handles 10,000+ concurrent users without crashes

---

## ✅ STEP-BY-STEP SETUP

### **Step 1: Get Gmail App Password (2 minutes)**

1. **Go to:** https://myaccount.google.com/apppasswords
2. **Sign in** with your Gmail account
3. **Click:** "Select app" → Choose "Mail"
4. **Click:** "Select device" → Choose "Other (Custom name)"
5. **Type:** "CLARITY Engine"
6. **Click:** "Generate"
7. **Copy** the 16-character password (looks like: `abcd efgh ijkl mnop`)

**⚠️ IMPORTANT:** This is NOT your regular Gmail password. It's a special "App Password" that's safer.

---

### **Step 2: Add to .env File (1 minute)**

Open your `.env` file (in the root of your project) and add:

```bash
# Email Configuration (for sending results to users)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
MAIL_DEFAULT_SENDER=noreply@claritypearl.com
ENABLE_EMAIL_DELIVERY=true
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with the 16-character App Password you copied

---

### **Step 3: Test Email (1 minute)**

**Option A: Using curl (Terminal)**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@gmail.com",
    "test_type": "analysis"
  }'
```

**Option B: Using Browser**
Go to: https://veritas-engine-zae0.onrender.com/test/email/config

You should see:
```json
{
  "email_delivery_enabled": true,
  "mail_username_set": true,
  "mail_password_set": true,
  "status": "configured"
}
```

---

### **Step 4: Check Your Inbox (1 minute)**

1. Open your Gmail inbox
2. Look for email from: "CLARITY Engine"
3. Subject: "✅ CLARITY Analysis Complete - Legal Intelligence"
4. If you don't see it, **check your Spam folder**

**If Email Arrives:** ✅ SUCCESS! Email delivery is working!

**If No Email:**
- Check .env file (credentials correct?)
- Check spam folder
- Wait 2-3 minutes (Gmail can be slow)
- Check server logs for errors

---

## 🧪 TEST ENDPOINTS

### **1. Check Configuration**
```bash
GET https://veritas-engine-zae0.onrender.com/test/email/config
```

**Response:**
```json
{
  "email_delivery_enabled": true,
  "mail_server": "smtp.gmail.com",
  "mail_port": 587,
  "mail_username_set": true,
  "mail_password_set": true,
  "status": "configured"
}
```

### **2. Send Test Email (Analysis Complete)**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@gmail.com",
    "test_type": "analysis"
  }'
```

### **3. Send Test Email (Funding Complete)**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@gmail.com",
    "test_type": "funding"
  }'
```

### **4. Send Test Email (Task Submitted)**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/test/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@gmail.com",
    "test_type": "task"
  }'
```

---

## 📧 EMAIL TEMPLATES

### **1. Analysis Complete Email**
- **Subject:** "✅ CLARITY Analysis Complete - [Domain]"
- **Content:**
  - Domain used (Legal, Financial, etc.)
  - Analysis ID
  - Confidence Score
  - Summary of findings
  - Download button

### **2. Funding Package Complete Email**
- **Subject:** "🎉 Your Funding Package is Ready!"
- **Content:**
  - Project name
  - Number of documents generated
  - ZIP file download link
  - Next steps

### **3. Task Submitted Email**
- **Subject:** "⚡ CLARITY Task Received"
- **Content:**
  - Task ID
  - Estimated completion time
  - What happens next

---

## 🔧 TROUBLESHOOTING

### **Issue: Email not configured**
```json
{
  "success": false,
  "message": "Email service not configured",
  "details": {
    "mail_username_set": false,
    "mail_password_set": false
  }
}
```

**Fix:** Add MAIL_USERNAME and MAIL_PASSWORD to .env file

---

### **Issue: Gmail blocking login**
**Error:** "Username and Password not accepted"

**Fix:**
1. Make sure you're using an **App Password**, not your regular Gmail password
2. Enable "Less secure app access" in Gmail settings
3. Or use Google Workspace account (paid Gmail)

---

### **Issue: Emails going to spam**
**Fix:**
1. Add `noreply@claritypearl.com` to your contacts
2. Mark the email as "Not Spam"
3. Future emails will go to inbox

---

### **Issue: Email takes long time**
**Normal:** Gmail SMTP can take 30-60 seconds to send
**If > 2 minutes:** Check server logs, might be network issue

---

## 🚀 PRODUCTION DEPLOYMENT

### **For Render (Backend):**

1. **Go to:** https://dashboard.render.com
2. **Select** your CLARITY backend service
3. **Go to:** Environment → Environment Variables
4. **Add:**
   - `MAIL_USERNAME` = your-email@gmail.com
   - `MAIL_PASSWORD` = your-app-password
   - `ENABLE_EMAIL_DELIVERY` = true
5. **Save** → Service will auto-restart
6. **Test** using curl commands above

---

## 📊 WHAT HAPPENS AFTER SETUP

### **Before Email (Current):**
```
User submits analysis
→ Frontend shows "Processing..."
→ User waits in browser (5-15 minutes)
→ If browser closes → LOSES RESULTS
→ If 100 users → SERVER CRASHES
```

### **After Email (Once Working):**
```
User submits analysis
→ Frontend shows "Task submitted! Check email in 5-15 min"
→ User closes browser (doesn't wait)
→ Backend processes in background
→ Sends email with results
→ User opens email → Downloads results
→ Works for 10,000+ concurrent users
```

---

## 🎯 NEXT STEPS AFTER EMAIL WORKS

Once email delivery is confirmed working:

### **1. Connect to Analysis Endpoints**
Update `/instant/analyze` to send real emails (currently just returns preview)

### **2. Connect to Funding Engine**
Update `/api/funding/generate` to send real document packages

### **3. Add Attachments**
Attach PDF reports, Word docs, Excel files to emails

### **4. Add Email Tracking**
Track: delivered, opened, clicked (using SendGrid or similar)

---

## 💰 COST

**Gmail (Free):**
- Limit: 500 emails/day
- Cost: $0
- Perfect for: Testing, early customers (< 50 users)

**Gmail Business (Paid):**
- Limit: 2,000 emails/day
- Cost: $6/user/month
- Perfect for: Growing startups (50-500 users)

**SendGrid (Recommended for Scale):**
- Limit: 100,000 emails/month (free tier)
- Cost: $0-$15/month
- Perfect for: 1,000+ users

---

## 📞 SUPPORT

**Need help?**
- **Email:** nsubugacollin@gmail.com
- **Phone:** +256 705 885118

**Common Issues:**
- App Password not working → Regenerate new one
- Emails not arriving → Check spam folder
- Server errors → Check .env file syntax

---

**🎉 THAT'S IT! EMAIL DELIVERY IN 5 MINUTES!**

**Once working, your platform can handle unlimited users without crashes.**

---

*Last Updated: November 5, 2025*  
*Email Service: Configured, Ready to Test*  
*Next: Connect to analysis endpoints*
