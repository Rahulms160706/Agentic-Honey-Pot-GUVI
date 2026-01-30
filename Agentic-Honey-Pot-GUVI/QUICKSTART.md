# Quick Start Guide - Agentic Honey-Pot

Get your Agentic Honey-Pot system running in 5 minutes!

## 🚀 Fastest Way to Start

### Option 1: Docker (Recommended)

```bash
# 1. Navigate to project directory
cd agentic-honeypot

# 2. Start the service
docker-compose up -d

# 3. Check if it's running
curl http://localhost:8000/health

# Done! 🎉
```

### Option 2: Python (Local Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python main.py

# 3. Test it
curl http://localhost:8000/health

# Done! 🎉
```

## 🧪 Test Immediately

### Quick Test with cURL

```bash
# Test a scam message
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345" \
  -d '{
    "sessionId": "quick-test-123",
    "message": {
      "sender": "scammer",
      "text": "URGENT! Your account will be blocked. Share OTP now!",
      "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

### Run Full Test Suite

```bash
python test_scenarios.py
```

This will run 6 different scam scenarios automatically!

## 📊 Expected Output

You should see:
```json
{
  "status": "success",
  "reply": "Why is my account being blocked?",
  "scamDetected": true,
  "confidenceScore": 0.85
}
```

## 🔧 Configuration

### Change API Key

Edit `main.py` line 27:
```python
API_KEY = "YOUR_SECRET_API_KEY_12345"  # Change this!
```

Or use environment variable:
```bash
export API_KEY="your-new-key"
python main.py
```

## 📡 API Endpoints

- **Health Check:** `GET http://localhost:8000/health`
- **Process Message:** `POST http://localhost:8000/api/message`
- **Get Session:** `GET http://localhost:8000/api/session/{sessionId}`

## 📝 Request Format

```json
{
  "sessionId": "unique-id",
  "message": {
    "sender": "scammer",
    "text": "Your message here",
    "timestamp": "2026-01-29T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

## 🎯 What It Does

1. **Detects Scams** - Analyzes messages for scam indicators
2. **Engages Scammers** - AI agent responds like a real person
3. **Extracts Intel** - Collects UPI IDs, bank accounts, phone numbers, links
4. **Reports Results** - Sends findings to GUVI endpoint

## 🛠️ Troubleshooting

### Port 8000 Already in Use?
```bash
# Change port in main.py or docker-compose.yml
# OR kill existing process:
lsof -i :8000
kill -9 <PID>
```

### Docker Not Working?
```bash
# Check Docker is running:
docker --version
docker-compose --version

# Restart Docker service
sudo systemctl restart docker
```

### API Key Not Working?
```bash
# Check you're using the correct key:
# Default: YOUR_SECRET_API_KEY_12345
# Header: x-api-key: YOUR_SECRET_API_KEY_12345
```

## 📚 Next Steps

1. **Read README.md** - Comprehensive documentation
2. **Check DOCUMENTATION.md** - Architecture details
3. **Review DEPLOYMENT.md** - Production deployment guide
4. **Import postman_collection.json** - Test with Postman

## 🎉 You're Ready!

Your Agentic Honey-Pot is now running and ready to detect scams!

Test it with the provided scenarios or integrate it with your evaluation platform.

---

**Need Help?**
- Check logs: `docker-compose logs -f` (Docker) or console output (Python)
- Review README.md for detailed documentation
- Test with: `python test_scenarios.py`
