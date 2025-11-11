# 🚀 CLARITY Setup Guide

## Complete Setup Instructions for Fortune 50-Grade AI Platform

---

## 📋 Prerequisites

### Required Software
- **Python 3.9+**
- **PostgreSQL 12+**
- **Redis 6+**
- **Git**

### Optional (for advanced features)
- **ChromaDB** (for Intelligence Vault)
- **Docker** (for containerized deployment)

---

## 🔧 Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd clarity
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

### Required Environment Variables:
```env
# MUST HAVE (Minimum to run)
DATABASE_URL=postgresql://postgres:password@localhost:5432/clarity_db
GOOGLE_API_KEY=your-google-api-key-here
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
FLASK_SECRET_KEY=your-secret-key-here
```

### Recommended (Multi-LLM Failover):
```env
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GROQ_API_KEY=your-groq-key-here
```

---

## 🗄️ Database Setup

### 1. Create PostgreSQL Database
```bash
# Log into PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE clarity_db;

# Exit psql
\q
```

### 2. Run Migrations
```bash
# Initialize migrations (if not already done)
flask db init

# Create migration
flask db migrate -m "Initial setup"

# Apply migrations
flask db upgrade
```

---

## 🔑 Getting API Keys

### Google Gemini API (REQUIRED)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and add to `.env`:
   ```
   GOOGLE_API_KEY=your-key-here
   ```

### OpenAI API (Optional - Failover)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new secret key
3. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

### Anthropic Claude API (Optional - Failover)
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Generate API key
3. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Groq API (Optional - Ultra-Fast)
1. Go to [Groq Console](https://console.groq.com/)
2. Create API key
3. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

---

## ▶️ Running CLARITY

### Start Services

You need **3 terminal windows**:

#### Terminal 1: Redis
```bash
redis-server
```

#### Terminal 2: ChromaDB (for Intelligence Vault)
```bash
chroma run --path ./chroma_data
```

#### Terminal 3: Flask Application
```bash
python run.py
```

#### Terminal 4: Celery Worker
```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

### Access CLARITY
- **Web Interface**: http://localhost:5000
- **API**: http://localhost:5000/api
- **API Docs**: http://localhost:5000/api-management/documentation

---

## 👤 Create Your First User

### Option 1: Web Registration
1. Go to http://localhost:5000
2. Click "Get Started"
3. Register with email and password

### Option 2: Python Shell
```bash
python
```

```python
from app import create_app, db
from app.models import User, Subscription

app = create_app()
with app.app_context():
    # Create user
    user = User(email='admin@clarity.ai', password='secure-password')
    db.session.add(user)
    db.session.commit()
    
    # Create subscription
    sub = Subscription(
        user_id=user.id,
        tier='enterprise',  # or 'free' or 'pro'
        status='active'
    )
    db.session.add(sub)
    db.session.commit()
    
    print(f"User created with ID: {user.id}")
```

---

## 🔑 Generate API Key for Client Access

### Via Web Interface
1. Log in to CLARITY
2. Go to http://localhost:5000/api-management/dashboard
3. Click "Generate New API Key"
4. **SAVE THE KEY IMMEDIATELY** (shown only once)

### Via Python
```python
from app import create_app, db
from app.models import APIKey, User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@clarity.ai').first()
    
    # Generate API key
    new_key, hashed_key = APIKey.generate_key()
    
    api_key_record = APIKey(user_id=user.id)
    api_key_record.key_hash = hashed_key
    api_key_record.is_active = True
    
    db.session.add(api_key_record)
    db.session.commit()
    
    print(f"API Key: {new_key}")
```

---

## 🧪 Testing the API

### Test with cURL
```bash
# Replace YOUR_API_KEY with your actual key
curl -X POST http://localhost:5000/api/analyze \
  -H "X-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_directive": "Analyze this text",
    "uploaded_files": [{
      "filename": "test.txt",
      "content_base64": "VGVzdCBjb250ZW50",
      "content_type": "text/plain"
    }]
  }'
```

### Test with Python
```python
import requests
import base64

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:5000/api"

# Analyze a document
response = requests.post(
    f"{BASE_URL}/analyze",
    headers={"X-API-KEY": API_KEY},
    json={
        "user_directive": "Analyze this document",
        "uploaded_files": [{
            "filename": "test.txt",
            "content_base64": base64.b64encode(b"Test content").decode(),
            "content_type": "text/plain"
        }]
    }
)

print(response.json())
```

---

## 🎨 Frontend & Templates

### Available Pages
- **Landing Page**: `/` - Public homepage
- **Dashboard**: `/dashboard` - User dashboard
- **API Management**: `/api-management/dashboard` - Manage API keys
- **API Docs**: `/api-management/documentation` - Full API documentation
- **Login**: `/auth/login`
- **Register**: `/auth/register`

### Customization
Edit templates in `/app/templates/`:
- `landing.html` - Homepage
- `base.html` - Base template
- `api_management/` - API management pages

---

## 🐳 Docker Deployment (Optional)

### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🔒 Security Best Practices

### In Production:
1. **Change SECRET_KEY**: Use a strong random key
2. **Set DEBUG=False**: Never run debug mode in production
3. **Use HTTPS**: Set up SSL/TLS certificates
4. **Secure Database**: Use strong passwords, restrict access
5. **API Rate Limiting**: Configure appropriate limits
6. **Environment Variables**: Never commit `.env` to git
7. **Regular Updates**: Keep dependencies updated

---

## 📊 Monitoring & Maintenance

### Check Celery Tasks
```bash
# Monitor with Flower
celery -A celery_worker.celery_app flower
# Access at http://localhost:5555
```

### View Logs
```bash
# Application logs
tail -f logs/clarity.log

# Celery logs
# Check terminal where celery worker is running
```

### Database Maintenance
```bash
# Backup database
pg_dump clarity_db > clarity_backup.sql

# Restore database
psql clarity_db < clarity_backup.sql
```

---

## 🆘 Troubleshooting

### Issue: "No module named 'app'"
**Solution**: Make sure you're in the project root and virtual environment is activated

### Issue: "Connection refused" for Redis
**Solution**: Start Redis server: `redis-server`

### Issue: "Connection refused" for PostgreSQL
**Solution**: Ensure PostgreSQL is running: `sudo service postgresql start`

### Issue: "API key required"
**Solution**: Generate API key via `/api-management/dashboard` or Python shell

### Issue: "Import error for Google AI"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: Multi-LLM providers not working
**Solution**: Check that API keys are correctly set in `.env` file

---

## 🎓 Learning Resources

### Documentation
- `/api-management/documentation` - Full API docs
- `CLARITY_ULTIMATE_EMPIRE.md` - Complete platform overview
- `.env.example` - All environment variables explained

### Example Code
- Check `app/api/routes.py` for API examples
- Check `app/data_science/` for data science examples
- Check `app/expense_management/` for expense tracking examples

---

## 🚀 Next Steps

1. ✅ Complete setup (you're here!)
2. 🔑 Generate API key
3. 🧪 Test API endpoints
4. 📊 Upload documents to Intelligence Vault
5. 🤖 Run first analysis
6. 💰 Try expense management features
7. 📈 Explore data science capabilities
8. 🌍 Deploy to production

---

## 💬 Support

- **Documentation**: Full docs at `/api-management/documentation`
- **Issues**: Create GitHub issue
- **Email**: support@clarity.ai (future)

---

**Built with excellence. Deployed with confidence. Scaled without limits.**

🏛️ **CLARITY - Fortune 50-Grade AI Intelligence Platform** 🏛️
