# CLARITY Engine - Professional Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CLARITY Engine** is a secure, AI-powered intelligence platform that automates the analysis of complex documents for high-value professionals. Transform billable hours wasted on reading into billable seconds spent on winning.

## 🚀 Features

### Core Intelligence
- **11 Specialized Domain Accelerators**: Legal, Financial, Security, Healthcare, Engineering, Government Proposals, Grant Proposals, Market Analysis, Pitch Decks, Investor Diligence, and Corporate Intelligence
- **Asynchronous Processing**: Handle 1000+ page documents without timeouts
- **Multi-Modal Analysis**: Process PDFs, DOCX, images, and text files
- **Real-Time Status Tracking**: Monitor analysis progress with live updates

### Security & Enterprise Features
- **Zero-Trust Authentication**: Secure user accounts with API key management
- **Rate Limiting**: Protect against abuse with configurable limits
- **CORS Support**: Secure cross-origin resource sharing
- **Comprehensive Logging**: Production-ready error tracking and monitoring
- **Environment Validation**: Fail-fast configuration validation

### Professional Interface
- **Modern Dashboard**: Dark-themed, responsive Command Deck
- **Drag-and-Drop Upload**: Intuitive file handling
- **JSON Results**: Structured, actionable intelligence reports
- **API Integration**: RESTful API for programmatic access

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Flask Web App   │───▶│  Redis Broker   │───▶│ Celery Workers  │
│  (Command Deck) │    │  (Gunicorn)      │    │  (Message Queue)│    │ (AI Processing)│
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │                        │
                                ▼                        ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │  PostgreSQL     │    │  Google Gemini  │    │  File Storage   │
                       │  (User Data)    │    │  (AI Engine)    │    │  (Documents)    │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- Google Generative AI API Key

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/clarity-engine.git
cd clarity-engine
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/clarity_db
DIRECT_URL=postgresql://username:password@localhost:5432/clarity_db

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Security Configuration
FLASK_SECRET_KEY=your_super_secret_key_here
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Optional: Rate Limiting Storage
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
```

### 5. Database Setup
```bash
# Initialize database migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

## 🚀 Running the Application

### Development Mode

1. **Start Redis** (if not already running):
```bash
redis-server
```

2. **Start Celery Worker** (in a separate terminal):
```bash
celery -A celery_worker.celery worker --loglevel=info
```

3. **Start Flask Application**:
```bash
python run.py
```

4. **Access the Application**:
   - Web Interface: http://localhost:5000
   - API Documentation: http://localhost:5000/api/setup/system-status

### Production Mode

Use the provided `build.sh` script for production deployment:

```bash
chmod +x build.sh
./build.sh
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_clarity.py --base-url http://localhost:5000
```

The test script will:
1. Register a test user
2. Generate an API key
3. Submit a sample analysis
4. Verify the results structure

## 📚 API Documentation

### Authentication
All API endpoints require an API key in the `X-API-KEY` header.

### Core Endpoints

#### Submit Analysis
```http
POST /api/analyze/start
Content-Type: multipart/form-data
X-API-KEY: your_api_key_here

{
  "files": [file1, file2, ...],
  "directive": "Your analysis directive"
}
```

**Response:**
```json
{
  "message": "Analysis initiated",
  "job_id": "abc123-def456-ghi789",
  "status_url": "/api/analyze/status/abc123-def456-ghi789"
}
```

#### Check Analysis Status
```http
GET /api/analyze/status/{job_id}
X-API-KEY: your_api_key_here
```

**Response:**
```json
{
  "state": "SUCCESS",
  "result": {
    "executive_summary": "Analysis summary...",
    "key_findings": ["Finding 1", "Finding 2"],
    "actionable_recommendations": ["Recommendation 1"],
    "confidence_score": "High",
    "data_gaps": ["Missing information"]
  }
}
```

## 🎯 Domain Accelerators

### Legal Intelligence
- Contract analysis and risk assessment
- Evidence identification and case strategy
- Compliance verification and legal research

### Financial Intelligence
- Financial statement analysis
- Anomaly detection and fraud prevention
- Regulatory compliance verification

### Security Intelligence
- Multi-source intelligence fusion
- Threat assessment and timeline reconstruction
- Evidence correlation and risk analysis

### Healthcare Intelligence
- Medical record analysis
- Clinical trial evaluation
- HIPAA compliance auditing

### Government Proposal Intelligence
- RFP analysis and compliance mapping
- Capability matching and competitive positioning
- Proposal structure and content generation

### Engineering Intelligence
- Technical drawing analysis
- Specification verification and compliance
- Safety risk assessment

### Grant Proposal Intelligence
- Funder mission alignment
- Theory of Change formulation
- Impact metrics and storytelling

### Market Analysis Intelligence
- Market gap identification
- TAM calculation and competitive analysis
- Value proposition definition

### Pitch Deck Intelligence
- 10-slide investor presentation structure
- Business model and financial projections
- Competitive positioning and GTM strategy

### Investor Diligence Intelligence
- Weakness identification and risk mitigation
- Financial model validation
- Investor objection preparation

### Corporate Intelligence
- Strategic planning and market analysis
- M&A due diligence
- Performance evaluation and risk management

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `GOOGLE_API_KEY` | Google Generative AI API key | Yes | - |
| `CELERY_BROKER_URL` | Redis broker URL for Celery | Yes | - |
| `CELERY_RESULT_BACKEND` | Redis result backend URL | Yes | - |
| `FLASK_SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | No | * |
| `RATELIMIT_STORAGE_URL` | Rate limiting storage URL | No | memory:// |

### Rate Limiting

- Analysis submissions: 10 per minute per IP
- Status checks: 30 per minute per IP
- Configurable via `RATELIMIT_STORAGE_URL`

## 🚀 Deployment

### Render.com Deployment

1. **Create a new Web Service** on Render
2. **Connect your repository**
3. **Set environment variables** in the Render dashboard
4. **Deploy automatically** using the `build.sh` script

### Heroku Deployment

1. **Create a Heroku app**:
```bash
heroku create your-clarity-app
```

2. **Set environment variables**:
```bash
heroku config:set DATABASE_URL=your_postgres_url
heroku config:set GOOGLE_API_KEY=your_api_key
# ... other variables
```

3. **Deploy**:
```bash
git push heroku main
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## 📊 Monitoring

### Logs
- Application logs: `logs/clarity.log`
- Celery worker logs: Check worker terminal output
- Error tracking: Built-in Flask error handlers

### Health Checks
- System status: `GET /api/setup/system-status`
- Database connectivity: Automatic validation on startup
- Celery worker status: Monitor worker processes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/your-org/clarity-engine/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/clarity-engine/issues)
- **Email**: support@clarity.ai

## 🏆 Acknowledgments

- Google Generative AI for the powerful language model
- Flask community for the excellent web framework
- Celery team for robust task queue implementation
- All contributors and users of CLARITY Engine

---

**Built with ❤️ by the Pearl AI Team**

*Transforming professional intelligence, one document at a time.*
