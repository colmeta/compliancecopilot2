# 🌐 DEPLOY TO NETLIFY INSTEAD - 3 MINUTES

**Alternative to Vercel. Often handles Next.js better.**

---

## 📋 STEP-BY-STEP (DO THIS NOW)

### 1. **Create Netlify Account** (If you don't have one)
- Go to: https://app.netlify.com/signup
- Sign up with GitHub (easiest)

### 2. **Create New Site**
- Go to: https://app.netlify.com/
- Click "Add new site" → "Import an existing project"
- Click "GitHub"
- Authorize Netlify (if first time)
- Select: `colmeta/compliancecopilot2`

### 3. **Configure Build Settings**

**Base directory:**
```
frontend
```

**Build command:**
```
npm run build
```

**Publish directory:**
```
frontend/.next
```

**Functions directory:**
```
(leave empty)
```

### 4. **Environment Variables**

Click "Show advanced" → "New variable":

**Key:** `NEXT_PUBLIC_API_URL`  
**Value:** `https://veritas-engine-zae0.onrender.com`

### 5. **Deploy**
- Click "Deploy site"
- Wait 2-3 minutes
- **DONE!** ✅

---

## 🎯 YOUR NEW LINKS

Netlify will give you a URL like:

```
Landing Page:
https://clarity-engine-abc123.netlify.app/

Command Deck:
https://clarity-engine-abc123.netlify.app/work

Legal Analysis:
https://clarity-engine-abc123.netlify.app/work?domain=legal
```

### **Change URL (Optional):**
- Go to: Site settings → Domain management
- Click "Options" → "Edit site name"
- Change to: `clarity-engine` (if available)
- New URL: `https://clarity-engine.netlify.app`

---

## 🔥 WHY NETLIFY?

✅ **Better Next.js support** (sometimes)
✅ **More forgiving build process**
✅ **Great for free tier**
✅ **Automatic SSL**
✅ **Fast global CDN**

---

## 💡 CUSTOM DOMAIN (Optional)

**Add your own domain:**
- Go to: Domain settings
- Click "Add custom domain"
- Enter: `app.claritypearl.com` (or whatever)
- Point your DNS to Netlify (they give you instructions)
- Automatic SSL certificate provisioned

---

**NETLIFY IS OFTEN EASIER THAN VERCEL FOR COMPLEX NEXT.JS APPS.** ✅
