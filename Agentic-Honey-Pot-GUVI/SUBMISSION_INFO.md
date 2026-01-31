# 🔑 Honeypot API Submission Information

## API Endpoint Details

**Base URL:** `http://localhost:8000` (update with your deployed URL)  
**API Key:** `YOUR_SECRET_API_KEY_12345`  
**Authentication:** Header-based (`x-api-key`)

---

## 🧪 How to Test the Honeypot Endpoint

### Method 1: Using Swagger UI (Recommended)

1. Navigate to: **`http://localhost:8000/docs`**
2. Click the **🔓 Authorize** button at the top-right corner
3. Enter API Key: `YOUR_SECRET_API_KEY_12345`
4. Click **"Authorize"** and then **"Close"**
5. Now all endpoints are unlocked - try **POST /api/message**

### Method 2: Using cURL

```bash
curl -X POST "http://localhost:8000/api/message" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-001",
    "message": {
      "sender": "scammer",
      "text": "Hello! Your bank account has been suspended. Please verify your details immediately by clicking this link: http://fake-bank.com and send your OTP to 9876543210",
      "timestamp": "2026-01-31T12:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English"
    }
  }'
```

### Method 3: Using Postman

1. **Request Type:** POST
2. **URL:** `http://localhost:8000/api/message`
3. **Headers:**
   - `x-api-key`: `YOUR_SECRET_API_KEY_12345`
   - `Content-Type`: `application/json`
4. **Body (raw JSON):**
```json
{
  "sessionId": "test-session-001",
  "message": {
    "sender": "scammer",
    "text": "Urgent! Your account will be blocked. Call 9876543210 now.",
    "timestamp": "2026-01-31T12:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "WhatsApp"
  }
}
```

---

## ✅ What This Tests

- ✅ **API Authentication:** Validates x-api-key header
- ✅ **Endpoint Availability:** Confirms service is reachable
- ✅ **Scam Detection:** Analyzes message for scam indicators
- ✅ **AI Agent Response:** Returns intelligent, human-like reply
- ✅ **Intelligence Extraction:** Extracts UPI IDs, phone numbers, links
- ✅ **Response Structure:** Returns proper JSON format

---

## 📊 Expected Response

```json
{
  "status": "success",
  "reply": "Oh no! What should I do? Can you help me fix this?",
  "scamDetected": true,
  "confidenceScore": 0.85
}
```

---

## 🔍 View Extracted Intelligence

### Option 1: Dashboard (Visual)
Visit: **`http://localhost:8000/dashboard`**

### Option 2: API Endpoint
```bash
curl -X GET "http://localhost:8000/api/intelligence/test-session-001" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345"
```

**Response:**
```json
{
  "sessionId": "test-session-001",
  "scamDetected": true,
  "confidenceScore": 0.85,
  "messagesExchanged": 2,
  "extractedIntelligence": {
    "upiIds": [],
    "phoneNumbers": ["9876543210"],
    "phishingLinks": ["http://fake-bank.com"],
    "bankAccounts": [],
    "suspiciousKeywords": ["urgent", "blocked", "verify"]
  }
}
```

---

## 🛠️ All Available Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Root/Health check | ❌ |
| `/health` | GET | Detailed health status | ❌ |
| `/docs` | GET | Interactive API docs | ❌ |
| `/dashboard` | GET | Visual intelligence dashboard | ❌ |
| `/api/message` | POST | Main honeypot endpoint | ✅ |
| `/api/intelligence/{session_id}` | GET | Get extracted intelligence | ✅ |
| `/api/all-sessions` | GET | List all sessions | ✅ |
| `/api/session/{session_id}` | GET | Get full session details | ✅ |

---

## 🔐 Changing the API Key

### Option 1: Environment Variable
```bash
export API_KEY="your-custom-secure-key"
python main.py
```

### Option 2: Edit main.py
```python
API_KEY = os.getenv("API_KEY", "your-custom-secure-key")
```

---

## 📝 Notes for Evaluators

- **Default API Key:** `YOUR_SECRET_API_KEY_12345` (provided for testing)
- **Swagger UI Location:** `/docs` endpoint provides full interactive testing
- **No Authentication Needed For:** Root (`/`), health (`/health`), docs (`/docs`), dashboard (`/dashboard`)
- **Authentication Required For:** All `/api/*` endpoints
- **Response Time:** Typically < 2 seconds per request
- **Session Persistence:** In-memory (survives until server restart)

---

## 🚀 Deployment Notes

When deployed to production:
1. Update `Base URL` to your deployed endpoint
2. Set strong `API_KEY` via environment variable
3. Share API key securely with evaluators
4. Test connectivity using `/health` endpoint first
