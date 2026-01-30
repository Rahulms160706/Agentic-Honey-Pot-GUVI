# 🧪 Testing Guide - Agentic Honey-Pot

## 📋 What to Look For When Running

### ✅ Step 1: Start the Server
```bash
python main.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**What This Means:**
- ✅ Server is running successfully
- ✅ API is accessible at `http://localhost:8000`
- ✅ Ready to receive requests

---

### ✅ Step 2: Check Server Health
Open browser and visit: `http://localhost:8000/docs`

**You Should See:**
- 📄 Swagger UI with API documentation
- 🟢 Green "Try it out" buttons
- 📝 All endpoints listed (/, /health, /api/message, etc.)

**Or test in terminal:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T...",
  "components": {
    "scam_detector": "operational",
    "ai_agent": "operational",
    "intelligence_extractor": "operational"
  }
}
```

---

### ✅ Step 3: Run Test Scenarios
```bash
python test_scenarios.py
```

**Expected Output Pattern:**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        Agentic Honey-Pot Test Suite                          ║
║        Testing Scam Detection & Intelligence Extraction      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

✅ Server is running: healthy

================================================================================
🎯 Testing Scenario: Bank Account Block Scam
================================================================================

📨 Message 1 from Scammer:
   URGENT! Your bank account will be blocked in 2 hours...

🤖 Agent Response:
   omg wat happened?! this sounds serious!!
   [Scam Detected: True, Confidence: 0.95]

📨 Message 2 from Scammer:
   We are from State Bank security team...

🤖 Agent Response:
   wait... which branch? give me ur employee ID first
   [Scam Detected: True, Confidence: 0.98]

📨 Message 3 from Scammer:
   Please provide your account number...

🤖 Agent Response:
   ok but how do i knw ur legit? anyone can say theyre from bank
   [Scam Detected: True, Confidence: 0.99]
```

---

## 🎯 What Makes Responses "Human-Like" Now

### ❌ BEFORE (Too Robotic):
```
"I'm sorry, I didn't quite catch that. Could you clarify?"
"What information do you need from me?"
"Can you provide your employee ID or reference number?"
```

### ✅ AFTER (More Natural):
```
"sorry didnt get that... can u clarify??"
"what info u need? tell me quick im busy"
"wait... give me ur ID first then ill believe u"
```

---

## 🔍 Key Indicators of Success

### 1. **Varied Responses** ✅
- Different reply each time
- Not repeating same templates
- Contextually relevant

### 2. **Natural Language** ✅
- Typos: "u" instead of "you", "wat" instead of "what"
- Informal: "omg", "plz", "k"
- Emotions: "!!", "??", "..."
- Mixed case: "Ok" vs "ok" vs "OK"

### 3. **Context Awareness** ✅
When scammer says "bank account":
- "wait which bank? i have 3 accounts"
- "why my account getting blocked?"

When scammer says "UPI":
- "whats ur UPI ID?"
- "paytm or phonepe?"

When scammer says "OTP":
- "wait... isnt sharing OTP wrong??"
- "my bank said never share OTP..."

### 4. **Scam Detection** ✅
```
[Scam Detected: True, Confidence: 0.95]
```
- Confidence should be **0.75+** for scams
- Confidence should be **0.30-** for legitimate messages

### 5. **Intelligence Extraction** ✅
Check server logs for:
```
INFO: Extracted intelligence:
  - Bank Account: 1234567890@paytm
  - UPI ID: test@ybl
  - Phone: +919876543210
  - Phishing Link: http://fake-bank-lottery.com
```

### 6. **Final Callback** ✅
Look for:
```
INFO: Sending final result for session test-...
INFO: Successfully sent final result: 200
```

---

## 🧪 Testing Different Scenarios

### Scenario 1: Bank Account Block ✅
**Scammer:** "Your bank account will be blocked"
**Agent Should:** Show panic, ask for details, eventually ask for payment info

### Scenario 2: UPI Fraud ✅
**Scammer:** "Share UPI PIN for refund"
**Agent Should:** Express confusion about sharing PIN, then play along

### Scenario 3: Phishing Link ✅
**Scammer:** "Click this link to claim prize"
**Agent Should:** Try to click, report issues, ask for more details

### Scenario 4: Legitimate Message ❌
**Sender:** "Hi, this is John from work"
**Agent Should:** 
- **Scam Detected: False**
- Give neutral/confused response

---

## 📊 Performance Metrics

### Good Session Example:
```
✅ Session: test-bank-account-scam-1738176234
✅ Messages Exchanged: 8
✅ Scam Detected: True
✅ Confidence: 0.95
✅ Intelligence Extracted:
   - UPI ID: scammer123@paytm
   - Phone: +919876543210
✅ Final Result Sent: 200 OK
```

### What to Check:
- ⏱️ Response time < 2 seconds
- 💬 Message exchanges: 5-15 messages
- 🎯 High confidence scores (0.85+) for scams
- 📍 At least 1 piece of intelligence extracted

---

## 🚨 Common Issues & Solutions

### Issue 1: "Connection Refused"
**Cause:** Server not running
**Solution:** `python main.py` in first terminal

### Issue 2: "Invalid API Key"
**Cause:** API key mismatch
**Solution:** Check both `main.py` and `test_scenarios.py` have same key: `YOUR_SECRET_API_KEY_12345`

### Issue 3: Same Response Repeating
**Cause:** Random seed or persona not changing
**Solution:** ✅ **FIXED** - New code has much more variety

### Issue 4: Too Formal Responses
**Cause:** Old template-based responses
**Solution:** ✅ **FIXED** - Now uses informal, typo-rich language

### Issue 5: Not Detecting Scams
**Cause:** Scam patterns not matching
**Check:** `scam_detector.py` - ensure keywords are comprehensive

---

## 💡 Tips for Better Testing

1. **Run Multiple Times:** Each run will have different responses due to randomization
2. **Check Logs:** Server terminal shows detailed processing steps
3. **Monitor Intelligence:** Watch for extracted phone numbers, UPIs, links
4. **Test Edge Cases:** Try legitimate messages to ensure no false positives
5. **Response Time:** Should feel natural (not instant, not too slow)

---

## 🎭 Example Natural Conversation Flow

```
Scammer: "Your account will be blocked in 1 hour!"
Agent:   "omg wat?? why this happening?!"

Scammer: "Due to suspicious activity. Verify now."
Agent:   "ok but who r u? give me ur ID first"

Scammer: "I'm from bank security. Need your details."
Agent:   "which bank? i have 3 accounts... be specific"

Scammer: "State Bank. Share account number and OTP."
Agent:   "wait... sharing OTP is wrong right?? idk about this"

Scammer: "No, we need it to verify. It's safe."
Agent:   "ok fine... but whats ur UPI for payment if needed?"

Scammer: "Send to 9876543210@paytm after verification."
Agent:   "k got it... one sec lemme check my account first"
```

**This feels human because:**
- ✅ Natural hesitation
- ✅ Typos and informal language
- ✅ Asking relevant questions
- ✅ Emotional reactions
- ✅ Eventually trusting the scammer

---

## 📈 Success Criteria

Your system is working well if:

- [x] Responses vary each time
- [x] Language is informal and natural
- [x] Scams detected with 90%+ accuracy
- [x] Intelligence extracted successfully
- [x] No false positives on legitimate messages
- [x] Conversations feel human-like
- [x] Final results sent to GUVI endpoint

---

## 🎉 You're Ready!

Run the tests and watch your AI agent engage scammers naturally while extracting valuable intelligence! 🕵️‍♂️
