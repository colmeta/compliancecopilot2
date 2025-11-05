# 🔑 Getting API Keys for CLARITY - Complete Guide

## Your Complete Guide to Setting Up All LLM Providers

---

## 🎯 OVERVIEW

CLARITY uses **4 LLM providers** for maximum reliability:
1. **Google Gemini** (REQUIRED - Primary)
2. **OpenAI GPT-4** (OPTIONAL - High quality)
3. **Anthropic Claude** (OPTIONAL - Excellent quality)
4. **Groq** (OPTIONAL - Ultra-fast)

**You need AT LEAST Google Gemini to run CLARITY.**  
The others are optional but recommended for failover.

---

## 1️⃣ GOOGLE GEMINI API (REQUIRED)

### Why You Need It:
- Primary LLM provider
- Best balance of cost/speed/quality
- Required for CLARITY to work

### How to Get It:
1. **Go to**: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Click** "Create API Key"
4. **Copy** the key (starts with `AI...`)
5. **Add to .env**:
   ```env
   GOOGLE_API_KEY=AIza...your-key-here
   ```

### Cost:
- **Free Tier**: 60 requests per minute
- **Flash**: $0.075 per 1M input tokens
- **Pro**: $1.25 per 1M input tokens

### Test It:
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello!")
print(response.text)
```

---

## 2️⃣ OPENAI API (OPTIONAL - Recommended)

### Why You Need It:
- Industry-leading quality (GPT-4)
- Great for complex analysis
- Failover when Gemini is down

### How to Get It:
1. **Go to**: [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Sign up** or log in
3. **Add payment method** (required after free credits)
4. **Click** "Create new secret key"
5. **Copy** the key (starts with `sk-...`)
6. **Add to .env**:
   ```env
   OPENAI_API_KEY=sk-...your-key-here
   ```

### Cost:
- **GPT-4 Turbo**: $10 per 1M input tokens, $30 per 1M output
- **GPT-3.5 Turbo**: $0.50 per 1M input tokens, $1.50 per 1M output
- **Free Credits**: $5 for new accounts (expires after 3 months)

### Test It:
```python
import openai

client = openai.OpenAI(api_key="YOUR_KEY")
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## 3️⃣ ANTHROPIC CLAUDE API (OPTIONAL - Recommended)

### Why You Need It:
- Excellent quality (on par with GPT-4)
- Very good at complex reasoning
- Another failover option

### How to Get It:
1. **Go to**: [Anthropic Console](https://console.anthropic.com/)
2. **Sign up** or log in
3. **Add payment method**
4. **Go to** "API Keys"
5. **Click** "Create Key"
6. **Copy** the key (starts with `sk-ant-...`)
7. **Add to .env**:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...your-key-here
   ```

### Cost:
- **Claude 3.5 Sonnet**: $3 per 1M input tokens, $15 per 1M output
- **Claude 3 Haiku**: $0.25 per 1M input tokens, $1.25 per 1M output
- **Free Credits**: $5 for new accounts

### Test It:
```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
```

---

## 4️⃣ GROQ API (OPTIONAL - For Speed)

### Why You Need It:
- **FASTEST** inference (up to 500 tokens/second)
- Free tier is generous
- Great for simple, quick tasks

### How to Get It:
1. **Go to**: [Groq Console](https://console.groq.com/)
2. **Sign up** with Google/GitHub
3. **Go to** "API Keys"
4. **Click** "Create API Key"
5. **Copy** the key (starts with `gsk_...`)
6. **Add to .env**:
   ```env
   GROQ_API_KEY=gsk_...your-key-here
   ```

### Cost:
- **FREE TIER**: 30 requests per minute
- **Paid**: Very cheap (details TBA)

### Test It:
```python
from groq import Groq

client = Groq(api_key="YOUR_KEY")
response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## 🔒 SECURITY BEST PRACTICES

### DO:
✅ Store keys in `.env` file  
✅ Add `.env` to `.gitignore`  
✅ Use environment variables in code  
✅ Rotate keys regularly (every 90 days)  
✅ Monitor API usage for anomalies  

### DON'T:
❌ Commit keys to git  
❌ Share keys publicly  
❌ Hardcode keys in source code  
❌ Use the same key across multiple apps  
❌ Leave unused keys active  

---

## 📊 COST COMPARISON

| Provider | Model | Input (per 1M) | Output (per 1M) | Speed | Quality |
|----------|-------|----------------|-----------------|-------|---------|
| **Groq** | Llama 3.1 70B | FREE | FREE | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| **Gemini** | Flash | $0.075 | $0.30 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| **Gemini** | Pro | $1.25 | $5.00 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| **OpenAI** | GPT-3.5 | $0.50 | $1.50 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| **OpenAI** | GPT-4 Turbo | $10.00 | $30.00 | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| **Claude** | Haiku | $0.25 | $1.25 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| **Claude** | Sonnet | $3.00 | $15.00 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |

---

## 🎯 RECOMMENDED SETUP

### Minimum (Free):
```env
GOOGLE_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```
**Cost**: Mostly free  
**Reliability**: Good (2 providers)

### Recommended (Pro):
```env
GOOGLE_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
```
**Cost**: ~$50-100/month (depending on usage)  
**Reliability**: Excellent (3 providers)

### Enterprise (Best):
```env
GOOGLE_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key
GROQ_API_KEY=your-groq-key
```
**Cost**: ~$100-500/month (depending on usage)  
**Reliability**: Maximum (4 providers)

---

## 🧪 TESTING YOUR KEYS

### Test All Providers at Once:
```python
from app.llm_router import get_llm_router

router = get_llm_router()

# This will show which providers are available
status = router.get_provider_status()

print(f"Total providers: {status['total_providers']}")
print(f"Available: {status['available_providers']}")

for provider in status['providers']:
    print(f"- {provider['name']}: {'✅' if provider['available'] else '❌'}")
```

---

## 📞 HELP & TROUBLESHOOTING

### Error: "API key not found"
**Solution**: Check that key is in `.env` file with correct name

### Error: "Invalid API key"
**Solution**: Key might be expired or incorrect. Generate new one.

### Error: "Rate limit exceeded"
**Solution**: You hit free tier limit. Wait or upgrade.

### Error: "Provider connection failed"
**Solution**: Check internet connection. CLARITY will auto-failover.

---

## 🎓 EXAMPLE .env FILE

Here's a complete example with all LLM keys:

```env
# ==============================================================================
# CLARITY LLM API KEYS
# ==============================================================================

# Google Gemini (REQUIRED)
GOOGLE_API_KEY=AIzaSyD...your-key-here

# OpenAI (OPTIONAL)
OPENAI_API_KEY=sk-proj-...your-key-here

# Anthropic Claude (OPTIONAL)
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here

# Groq (OPTIONAL)
GROQ_API_KEY=gsk_...your-key-here

# ==============================================================================
# OTHER REQUIRED KEYS
# ==============================================================================

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/clarity_db

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Flask
FLASK_SECRET_KEY=your-secret-key-change-this
```

---

## 🚀 QUICK START CHECKLIST

- [ ] Get Google Gemini API key (REQUIRED)
- [ ] Get Groq API key (FREE, recommended)
- [ ] Get OpenAI API key (OPTIONAL)
- [ ] Get Anthropic API key (OPTIONAL)
- [ ] Add all keys to `.env` file
- [ ] Test keys with test script
- [ ] Start CLARITY
- [ ] Generate CLARITY API key for clients
- [ ] Test API endpoints

---

**Once you have at least Google Gemini API key, you're ready to run CLARITY!**

**The multi-LLM failover system will automatically use the best available provider.**

🏛️ **CLARITY - Never Goes Down** 🏛️
