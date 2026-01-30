# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered honeypot system that autonomously detects and engages with scammers to extract actionable intelligence.

## 🎯 Overview

This system implements an intelligent honeypot that:
- Detects scam intent from incoming messages
- Activates an autonomous AI Agent when scams are detected
- Maintains believable human-like personas
- Handles multi-turn conversations naturally
- Extracts scam-related intelligence (UPI IDs, bank accounts, phone numbers, phishing links)
- Reports findings to the GUVI evaluation endpoint

## 🏗️ Architecture

```
┌─────────────────┐
│  Incoming Msg   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scam Detector  │  ← Pattern matching + AI analysis
└────────┬────────┘
         │
         ▼
    Is Scam?
         │
         ├─ Yes ──▶ ┌──────────────────┐
         │          │   AI Agent       │  ← Human-like engagement
         │          │  (Multi-persona) │
         │          └────────┬─────────┘
         │                   │
         │                   ▼
         │          ┌──────────────────┐
         │          │ Intelligence     │  ← Extract intel
         │          │   Extractor      │
         │          └────────┬─────────┘
         │                   │
         │                   ▼
         │          ┌──────────────────┐
         │          │  GUVI Callback   │  ← Report results
         │          └──────────────────┘
         │
         └─ No ───▶ Safe Response
```

## 📦 Components

### 1. **main.py**
- FastAPI application with REST API endpoints
- Session management
- API authentication
- Callback handling

### 2. **scam_detector.py**
- Pattern-based scam detection
- Analyzes urgency, threats, suspicious requests
- Confidence scoring
- Multi-indicator detection

### 3. **ai_agent.py**
- Autonomous conversation agent
- Multiple personas (elderly, cautious, naive, busy professional)
- Dynamic strategy selection
- Human-like response generation
- Conversation termination logic

### 4. **intelligence_extractor.py**
- Extracts UPI IDs, bank accounts, phone numbers, URLs
- Pattern matching with validation
- Contextual intelligence extraction
- Suspicious keyword tracking

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone and navigate to project directory**
```bash
cd agentic-honeypot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
Edit `main.py` and set your API key:
```python
API_KEY = "YOUR_SECRET_API_KEY_12345"
```

4. **Run the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Check logs**
```bash
docker-compose logs -f
```

3. **Stop the service**
```bash
docker-compose down
```

## 📡 API Documentation

### Authentication
All requests require an API key in the header:
```
x-api-key: YOUR_SECRET_API_KEY_12345
Content-Type: application/json
```

### Endpoints

#### 1. Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T10:00:00Z",
  "components": {
    "scam_detector": "operational",
    "ai_agent": "operational",
    "intelligence_extractor": "operational"
  }
}
```

#### 2. Process Message
```bash
POST /api/message
```

**Request (First Message):**
```json
{
  "sessionId": "abc123-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-29T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Why is my account being blocked?",
  "scamDetected": true,
  "confidenceScore": 0.85
}
```

**Request (Follow-up Message):**
```json
{
  "sessionId": "abc123-session-id",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": "2026-01-29T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": "2026-01-29T10:15:30Z"
    },
    {
      "sender": "user",
      "text": "Why is my account being blocked?",
      "timestamp": "2026-01-29T10:16:10Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

#### 3. Get Session Details
```bash
GET /api/session/{session_id}
```

Headers:
```
x-api-key: YOUR_SECRET_API_KEY_12345
```

Response:
```json
{
  "sessionId": "abc123-session-id",
  "session": {
    "messages": [...],
    "scam_detected": true,
    "confidence_score": 0.85,
    "intelligence": {
      "bankAccounts": ["1234****5678"],
      "upiIds": ["scammer@paytm"],
      "phishingLinks": ["http://malicious-site.com"],
      "phoneNumbers": ["+911234567890"],
      "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
    },
    "agent_notes": ["Uses urgency tactics", "Requests sensitive data"],
    "created_at": "2026-01-29T10:15:30Z"
  }
}
```

## 🧪 Testing

### Using cURL

**Test scam message:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "sender": "scammer",
      "text": "URGENT! Your bank account will be blocked. Click here to verify: http://fake-bank.com",
      "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Test legitimate message:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345" \
  -d '{
    "sessionId": "test-session-456",
    "message": {
      "sender": "scammer",
      "text": "Hello, how are you today?",
      "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000/api/message"
API_KEY = "YOUR_SECRET_API_KEY_12345"

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Test scam message
payload = {
    "sessionId": "python-test-123",
    "message": {
        "sender": "scammer",
        "text": "Your UPI transaction of Rs.50,000 failed. Share OTP to reverse.",
        "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "WhatsApp",
        "language": "English",
        "locale": "IN"
    }
}

response = requests.post(API_URL, json=payload, headers=headers)
print(response.json())
```

## 🎭 AI Agent Personas

The agent uses different personas based on the conversation stage:

### 1. **Cautious Persona**
- Used in early messages
- Asks verification questions
- Appears skeptical but engaged

### 2. **Naive Persona**
- Used in middle-late stage
- Shows trust and concern
- Easier to extract information from

### 3. **Elderly Persona**
- Confused about technology
- Asks for step-by-step help
- Builds scammer's confidence

### 4. **Busy Professional**
- Rushed but concerned
- Wants quick resolution
- Pragmatic approach

## 🎯 Engagement Strategies

The agent dynamically selects strategies:

1. **Ask for Details** - Gather information about the scam
2. **Request Verification** - Ask for proof of legitimacy
3. **Play Along** - Appear cooperative to extract intel
4. **Express Confusion** - Get scammer to reveal more
5. **Show Urgency** - Make scammer comfortable
6. **Request Payment Details** - Extract critical intelligence

## 🔍 Intelligence Extraction

### Extracted Data Types

1. **UPI IDs**: `username@paytm`, `user@ybl`
2. **Bank Accounts**: Masked format `1234****5678`
3. **Phone Numbers**: Formatted as `+91XXXXXXXXXX`
4. **Phishing Links**: Full URLs of malicious sites
5. **Suspicious Keywords**: Scam tactics and techniques

### Validation & Cleaning

- UPI IDs validated against known providers
- Phone numbers standardized to international format
- Bank accounts masked for privacy
- URLs sanitized and validated
- Keywords categorized by scam type

## 📊 Final Result Callback

When sufficient intelligence is extracted, the system automatically sends results to GUVI:

```json
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult

{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": ["1234****5678"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://malicious-site.com"],
    "phoneNumbers": ["+911234567890"],
    "suspiciousKeywords": ["urgent", "verify now", "otp_fraud"]
  },
  "agentNotes": "Uses urgency tactics and payment redirection | Impersonates bank official"
}
```

### When Callback is Triggered

- After 8+ messages if payment info extracted
- After 15 messages regardless of intel
- When scammer becomes suspicious
- When conversation naturally ends

## 🔒 Security & Ethics

### ✅ Implemented Safeguards

- No impersonation of real individuals
- No illegal instructions provided
- No harassment of any kind
- Responsible data handling
- Privacy-conscious (account masking)
- API key authentication

### ⚠️ Important Notes

- This is for **research and defensive purposes only**
- Extracted intelligence should be used **responsibly**
- Report findings to **appropriate authorities**
- Do not use for **offensive operations**

## 🐛 Troubleshooting

### API Key Issues
```
Error: Invalid API key
Solution: Check x-api-key header matches API_KEY in main.py
```

### Port Already in Use
```
Error: Address already in use
Solution: Change port in main.py or kill existing process
```

### Connection Timeout
```
Error: Connection timeout
Solution: Check firewall settings and server status
```

## 📈 Evaluation Criteria

Your solution will be evaluated on:

1. **Scam Detection Accuracy** (25%)
   - True positive rate
   - False positive rate
   - Confidence scoring

2. **Agentic Engagement Quality** (30%)
   - Human-like responses
   - Conversation flow
   - Persona consistency
   - Strategic adaptation

3. **Intelligence Extraction** (25%)
   - Accuracy of extracted data
   - Completeness of intelligence
   - Validation quality

4. **API Stability** (10%)
   - Response time
   - Error handling
   - Uptime

5. **Ethical Behavior** (10%)
   - Compliance with constraints
   - Responsible data handling
   - No harmful actions

## 🚀 Deployment Options

### 1. Local Development
```bash
python main.py
```

### 2. Docker Container
```bash
docker-compose up -d
```

### 3. Cloud Deployment (AWS/GCP/Azure)
- Deploy Docker container to cloud service
- Configure load balancer
- Set up monitoring
- Enable auto-scaling

### 4. Serverless (AWS Lambda)
- Package as Lambda function
- Use API Gateway
- Configure triggers
- Set up CloudWatch logging

## 📝 Configuration

### Environment Variables
```bash
export API_KEY="your-secret-key"
export GUVI_CALLBACK_URL="https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
export LOG_LEVEL="INFO"
export PORT="8000"
```

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve detection algorithms

## 📄 License

This project is for educational and research purposes only.

## 👥 Team

Built for GUVI Hackathon - AI for Fraud Detection & User Safety

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API documentation above
- Test with provided cURL commands

---

**🎯 One-Line Summary:**
Build an AI-powered agentic honeypot API that detects scam messages, engages scammers in multi-turn conversations, extracts intelligence, and reports the final result back to the GUVI evaluation endpoint.
