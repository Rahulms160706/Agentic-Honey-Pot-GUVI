"""
Manual Test Script for Dashboard
Send messages with intelligence and see them in the dashboard
"""
import requests
import time

API_URL = "http://localhost:8000/api/message"
API_KEY = "YOUR_SECRET_API_KEY_12345"  # Match the one in main.py

def send_message(session_id, sender, text, conversation_history=None):
    """Send a message to the API"""
    if conversation_history is None:
        conversation_history = []
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": sender,
            "text": text,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "conversationHistory": conversation_history,
        "metadata": {
            "channel": "SMS",
            "language": "en",
            "locale": "IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()

def test_scam_scenario():
    """Test a complete scam scenario with intelligence"""
    print("🧪 Testing Scam Scenario with Intelligence Extraction")
    print("=" * 70)
    
    session_id = f"manual-test-{int(time.time())}"
    conversation_history = []
    
    # Message 1: Initial contact
    print("\n📨 Message 1: Initial scam contact")
    response = send_message(
        session_id, 
        "scammer",
        "URGENT! Your bank account will be blocked. Contact us immediately!"
    )
    print(f"   Agent replied: {response['reply']}")
    
    conversation_history.append({
        "sender": "scammer",
        "text": "URGENT! Your bank account will be blocked. Contact us immediately!",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    time.sleep(1)
    
    # Message 2: UPI ID request
    print("\n📨 Message 2: Scammer shares UPI ID")
    response = send_message(
        session_id,
        "scammer", 
        "Please send Rs.1 to verify your account. Use this UPI: scammer123@paytm",
        conversation_history
    )
    print(f"   Agent replied: {response['reply']}")
    
    conversation_history.append({
        "sender": "scammer",
        "text": "Please send Rs.1 to verify your account. Use this UPI: scammer123@paytm",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    time.sleep(1)
    
    # Message 3: Phone number
    print("\n📨 Message 3: Scammer shares phone number")
    response = send_message(
        session_id,
        "scammer",
        "Call me on +919876543210 to verify your details immediately!",
        conversation_history
    )
    print(f"   Agent replied: {response['reply']}")
    
    conversation_history.append({
        "sender": "scammer",
        "text": "Call me on +919876543210 to verify your details immediately!",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    time.sleep(1)
    
    # Message 4: Phishing link
    print("\n📨 Message 4: Scammer shares phishing link")
    response = send_message(
        session_id,
        "scammer",
        "Click here to update KYC: http://fake-bank-kyc.com/update",
        conversation_history
    )
    print(f"   Agent replied: {response['reply']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Test completed! Session ID: {session_id}")
    print(f"🌐 View dashboard: http://localhost:8000/dashboard")
    print(f"📊 Check intelligence: http://localhost:8000/api/intelligence/{session_id}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/health")
        print("✅ Server is running!\n")
        
        # Run test
        test_scam_scenario()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server is not running!")
        print("   Start the server first: python main.py")
