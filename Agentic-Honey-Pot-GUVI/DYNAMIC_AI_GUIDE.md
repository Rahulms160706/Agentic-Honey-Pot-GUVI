# 🎯 Complete Data & AI Training Guide

## PART 1: WHERE IS YOUR DATA? (The Dashboard)

### Now You Have 3 Ways to See Extracted Data:

#### **Method 1: Web Dashboard (EASIEST) ✨**
1. Start server: `python main.py`
2. Open browser: `http://localhost:8000/dashboard`
3. **See all extracted UPI IDs, phone numbers, links, bank accounts in real-time!**

**Features:**
- 📊 Live stats (total scams detected, UPI IDs extracted, etc.)
- 🔄 Auto-refresh every 3 seconds
- 📋 Shows each session with all extracted intelligence
- 🎨 Beautiful UI with color-coded data

**IMPORTANT:** Change the API key in the dashboard:
```javascript
// In the dashboard page, find this line:
const API_KEY = "YOUR_SECRET_API_KEY_12345";  // Change this!
```
Change to your actual API key (same as in main.py)

---

#### **Method 2: API Endpoints**

**Get all sessions:**
```bash
curl -X GET "http://localhost:8000/api/all-sessions" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345"
```

**Get intelligence from specific session:**
```bash
curl -X GET "http://localhost:8000/api/intelligence/test-bank-account-block-scam-1769702419" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345"
```

**Response Example:**
```json
{
  "sessionId": "test-bank-scam-1769702419",
  "scamDetected": true,
  "confidenceScore": 0.95,
  "messagesExchanged": 5,
  "extractedIntelligence": {
    "upiIds": [
      "scammer123@paytm",
      "attacker@ybl"
    ],
    "phoneNumbers": [
      "+919876543210"
    ],
    "bankAccounts": [
      "1234****5678"
    ],
    "phishingLinks": [
      "http://fake-bank.com"
    ]
  }
}
```

---

#### **Method 3: Server Logs**
When you run `python test_scenarios.py`, check the server terminal:
```
INFO: Extracted intelligence: 
  {
    'upiIds': ['scammer@paytm'],
    'phoneNumbers': ['+919876543210'],
    ...
  }
```

---

## PART 2: DYNAMIC AI RESPONSES (The Real Question!)

### Current System: **Template-Based** ❌
```python
responses = [
    "ok whats ur UPI ID?",
    "give me ur UPI ID ill send now",
    "which app? paytm? gpay? phonepe?"
]
return random.choice(responses)  # Picks from fixed list
```

**Problems:**
- Limited to pre-written responses
- No context learning
- Same patterns repeat
- Not truly "AI"

---

### Solution: **Integrate with Real LLM APIs** ✅

You have several options:

## Option A: OpenAI GPT (Best Quality) 🏆

### Step 1: Install OpenAI library
```bash
pip install openai
```

### Step 2: Get API key from OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create account and add payment method
3. Create new API key
4. Copy it

### Step 3: Add to your `ai_agent.py`

```python
import openai
from typing import List, Dict, Any

class ScamEngagementAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        # ... rest of init
    
    async def generate_response(
        self,
        incoming_message: str,
        conversation_history: List[Dict],
        scam_indicators: List[str],
        session_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate dynamic response using GPT"""
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are a cautious but curious person who got a scam message.
                
IMPORTANT RULES:
1. Never share your actual bank details, OTP, or passwords
2. But ask QUESTIONS to extract their details (UPI ID, phone, bank account)
3. Sound human: use typos, lowercase, casual language like "u", "ur", "wat", "lol"
4. Be initially skeptical but gradually more trusting as scammer convinces you
5. Ask for their payment details, not yours
6. Keep responses SHORT (1-2 sentences max)

Make responses natural and human-like."""
            }
        ]
        
        # Add conversation history
        for msg in conversation_history:
            role = "user" if msg.get("sender") == "scammer" else "assistant"
            messages.append({
                "role": role,
                "content": msg.get("text", "")
            })
        
        # Get response from GPT
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" for better quality
                messages=messages,
                temperature=0.7,  # Some randomness for variety
                max_tokens=100
            )
            
            reply = response.choices[0].message.content.strip()
            return {
                "reply": reply,
                "strategy": "openai_gpt"
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to template-based if API fails
            return await self._fallback_response(incoming_message)
```

### Step 4: Update your `.env` or set environment variable
```bash
set OPENAI_API_KEY=sk-proj-xxxxx  # Windows
export OPENAI_API_KEY=sk-proj-xxxxx  # Linux/Mac
```

### Step 5: Update requirements.txt
```bash
pip install openai
pip freeze | grep openai >> requirements.txt
```

---

## Option B: Local LLM (Free, No API Key) 💰

Use **Ollama** (runs locally, no internet needed)

### Step 1: Download Ollama
https://ollama.ai

### Step 2: Pull a model
```bash
ollama pull mistral  # ~4GB, good quality
# or
ollama pull neural-chat  # Smaller, faster
```

### Step 3: Start Ollama
```bash
ollama serve
```

### Step 4: Use in your code
```python
import requests

async def generate_response_ollama(self, incoming_message: str, conversation_history: List[Dict]):
    """Generate response using local Ollama"""
    
    # Build prompt
    prompt = f"""You are a cautious person who received a scam message.
    
Never share OTP/password. Ask for THEIR details.
Sound human with typos and casual language.
Keep it SHORT (1-2 sentences).

Previous messages:
{chr(10).join([f"{msg['sender']}: {msg['text']}" for msg in conversation_history[-5:]])}

User response: {incoming_message}

Your reply (short and natural):"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': prompt,
                'stream': False,
            }
        )
        reply = response.json()['response'].strip()
        return reply
    except:
        return "ok what next?"
```

---

## Option C: Google Gemini API (Free tier available) 🎯

### Step 1: Install Google Generative AI
```bash
pip install google-generativeai
```

### Step 2: Get API key
https://makersuite.google.com/app/apikey

### Step 3: Use it
```python
import google.generativeai as genai

class ScamEngagementAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_response(self, incoming_message: str, conversation_history: List[Dict]):
        """Generate using Gemini"""
        prompt = f"""You are a person who got scammed before. You received: {incoming_message}
        
Be curious but careful. Ask for THEIR details (UPI, phone, bank).
Use casual language with typos: 'u', 'ur', 'wat', 'ok'.
Short replies only (1-2 sentences).
"""
        response = self.model.generate_content(prompt)
        return response.text
```

---

## COMPARISON

| Feature | Template (Current) | GPT-3.5 | Ollama (Local) | Gemini |
|---------|------------------|---------|-----------------|---------|
| **Cost** | Free ❌ | $0.001-0.002/msg | Free ❌ | Free tier ✅ |
| **Quality** | Low | Excellent ✅ | Good | Very Good ✅ |
| **Speed** | Instant | 1-2 sec | 2-5 sec | 1-2 sec |
| **Setup** | None | API key | Download app | API key |
| **Context Learning** | None | Somewhat | Somewhat | Yes ✅ |
| **Internet Needed** | No | Yes | No | Yes |

---

## RECOMMENDATION 🎁

**For Your Project, I Suggest:**

### **Best Choice: Google Gemini**
- ✅ Free API (12.5k requests/min)
- ✅ Good quality responses
- ✅ Easy to set up
- ✅ Fast responses

### **If You Want Best Quality: OpenAI GPT-4**
- ✅ Most intelligent responses
- ✅ Better conversation flow
- ❌ Costs money (~$0.01/msg)

### **If You Want Free & Local: Ollama**
- ✅ Completely free
- ✅ No internet needed
- ✅ Full privacy
- ❌ Slower responses (2-5 sec)

---

## IMPLEMENTATION STEPS

Want me to integrate one of these? Tell me which one and I'll:

1. ✅ Update `ai_agent.py` with LLM integration
2. ✅ Add system prompts to guide the AI
3. ✅ Add fallback (use templates if API fails)
4. ✅ Update `requirements.txt`
5. ✅ Test with your scenarios

---

## HOW IT WORKS (Simplified)

### Template (Current):
```
Scammer: "Send me Rs 1000"
Agent: picks random response from list → "ok where do i send?"
```

### LLM (New):
```
Scammer: "Send me Rs 1000"
System: "You're a curious person, protect your details, ask for theirs"
Agent: generates unique response → "ok but first tell me ur UPI ID"
Agent: (next time) → "which UPI should i use?"
Agent: (another variant) → "send ur details ill process"
```

Each response is **generated fresh** based on:
- ✅ The system prompt (your rules)
- ✅ Conversation history (context)
- ✅ Current message (what they said)
- ✅ Temperature (randomness level)

---

## SUMMARY

**Current State:**
- ✅ Data is now visible in beautiful dashboard
- ✅ Intelligence extraction works
- ❌ Responses are template-based

**What You Need:**
- Choose an LLM (GPT, Gemini, or Ollama)
- Tell me which one
- I'll integrate it

---

## NEXT STEPS

1. Go to `http://localhost:8000/dashboard` and verify you can see data
2. Decide which LLM to use (I recommend Gemini)
3. Let me know, and I'll integrate it!

Questions? Ask away! 🚀
