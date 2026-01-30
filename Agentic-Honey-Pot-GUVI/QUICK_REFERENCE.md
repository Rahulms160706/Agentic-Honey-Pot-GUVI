# ⚡ Quick Reference Card

## 🎯 The Absolute Shortest Path to Getting Started

### 3 Things You Need:
1. **Google API Key** (FREE)
2. **.env file** (1 line of text)
3. **Run 2 commands** (python main.py, python test_scenarios.py)

---

## 📋 Checklist

```
☐ Get API key from https://makersuite.google.com/app/apikey
☐ Copy the API key (starts with AIza...)
☐ Create file named ".env" in your project folder
☐ Add this line: GOOGLE_API_KEY=YOUR_KEY_HERE
☐ Save the .env file
☐ Open PowerShell in project folder
☐ Run: python main.py
☐ Wait for: ✅ Gemini API initialized successfully
☐ Open new PowerShell terminal
☐ Run: python test_scenarios.py
☐ Open: http://localhost:8000/dashboard
☐ See live data! 🎉
```

---

## 🔑 API Key (2 seconds)

```
1. Go to: https://makersuite.google.com/app/apikey
2. Click: Create API Key
3. Copy the key
4. Done!
```

---

## 📝 .env File (30 seconds)

**Create file:** `.env` (in project folder)

**Add one line:**
```
GOOGLE_API_KEY=YOUR_KEY_HERE
```

**Replace** `YOUR_KEY_HERE` with your actual key

**Save and close**

---

## ▶️ Run (2 commands)

### Terminal 1:
```powershell
python main.py
```

Wait for:
```
✅ Gemini API initialized successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 (new):
```powershell
python test_scenarios.py
```

You should see:
```
✅ Server is running: healthy
Generated response using Gemini API
🤖 Agent Response: [Dynamic response!]
```

### Browser:
```
http://localhost:8000/dashboard
```

---

## ✅ Success Signs

- ✅ Server terminal shows: `✅ Gemini API initialized successfully`
- ✅ Test output shows: `Generated response using Gemini API`
- ✅ Dashboard loads with live data
- ✅ Each response is DIFFERENT (not from template list)
- ✅ UPI IDs showing in dashboard

---

## 🆘 If It Doesn't Work

### Issue: "GOOGLE_API_KEY not set"
**Fix:** Make sure .env file exists with the API key

### Issue: "Invalid API key"  
**Fix:** Check the key from makersuite.google.com/app/apikey

### Issue: "Gemini API failed"
**Fix:** 
- Check internet connection
- Verify API key is correct
- Check server logs

### Issue: Still looks like templates?
**Fix:**
- Server should show "Gemini API initialized" ✅
- Tests should show "Generated response using Gemini API" ✅
- Each response should be different ✅

---

## 📖 Documentation

- **Quick Setup:** GEMINI_QUICKSTART.md
- **Full Guide:** GEMINI_SETUP.md
- **Improvements:** BEFORE_AFTER.md
- **Everything:** INTEGRATION_SUMMARY.md
- **Navigation:** INDEX.md

---

## ⏱️ Time Estimate

| Task | Time |
|------|------|
| Get API key | 2 min |
| Create .env | 1 min |
| Install packages | (already done) |
| Run server | 1 min |
| Run tests | 2 min |
| Check dashboard | 1 min |
| **TOTAL** | **~5-10 min** |

---

## 🚀 Commands You'll Use

```powershell
# Check Python
python --version

# Install packages
pip install -r requirements.txt

# Start server
python main.py

# Run tests
python test_scenarios.py

# Kill server (Ctrl+C)

# Check logs
# (in server terminal)
```

---

## 💡 That's It!

Just:
1. Get API key (2 min)
2. Create .env file (1 min)
3. Run 2 commands
4. View dashboard

Everything else is automatic!

---

## 🎯 What Happens Behind the Scenes

```
Your .env file
    ↓
python main.py reads .env
    ↓
Connects to Gemini API
    ↓
Initializes AI Agent
    ↓
Ready to receive messages
    ↓
Scammer sends message
    ↓
Gemini generates response (not from templates!)
    ↓
Intelligence extracted (UPI, phone, etc.)
    ↓
Dashboard shows live data
```

---

## ✨ Key Differences

| Old | New |
|-----|-----|
| Picks from 50 templates | Generates unlimited responses |
| Predictable | Creative |
| Limited context | Full context aware |
| Repeats after 3 msgs | Never repeats |
| Average 5 msgs | Average 12+ msgs |

---

## 📞 Need Help Quick?

1. **"How do I get API key?"** → https://makersuite.google.com/app/apikey
2. **"Where does .env go?"** → Project folder (same as main.py)
3. **"What goes in .env?"** → One line: GOOGLE_API_KEY=YOUR_KEY
4. **"How do I run it?"** → python main.py
5. **"Where's the dashboard?"** → http://localhost:8000/dashboard

---

## 🎉 You're Literally 5 Minutes Away!

- Get key → Create .env → Run → Done! 🚀

Let's go! 🚀
