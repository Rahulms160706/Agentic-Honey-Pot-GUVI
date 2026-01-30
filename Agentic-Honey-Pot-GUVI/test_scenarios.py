"""
Test Script for Agentic Honey-Pot System
Demonstrates various scam scenarios
"""
import requests
import json
import time
import os
from datetime import datetime

API_URL = "http://localhost:8000/api/message"
API_KEY = os.getenv("API_KEY", "YOUR_SECRET_API_KEY_12345")

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}


def test_scenario(scenario_name, messages):
    """Test a complete scam scenario"""
    print(f"\n{'='*80}")
    print(f"🎯 Testing Scenario: {scenario_name}")
    print(f"{'='*80}\n")
    
    session_id = f"test-{scenario_name.lower().replace(' ', '-')}-{int(time.time())}"
    conversation_history = []
    
    for i, scammer_message in enumerate(messages, 1):
        print(f"\n📨 Message {i} from Scammer:")
        print(f"   {scammer_message}")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scammer_message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "conversationHistory": conversation_history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            print(f"🤖 Agent Response:")
            print(f"   {result.get('reply', 'No reply')}")
            print(f"   [Scam Detected: {result.get('scamDetected', False)}, "
                  f"Confidence: {result.get('confidenceScore', 0):.2f}]")
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scammer_message,
                "timestamp": payload["message"]["timestamp"]
            })
            
            conversation_history.append({
                "sender": "user",
                "text": result.get('reply', ''),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # Small delay between messages
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break
    
    print(f"\n✅ Scenario completed. Session ID: {session_id}")
    print(f"{'='*80}\n")



import os
def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
            API_KEY = os.getenv("API_KEY", "12345")
    ║        Agentic Honey-Pot Test Suite                          ║
    ║        Testing Scam Detection & Intelligence Extraction      ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health")
        print(f"✅ Server is running: {health_response.json()['status']}\n")
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Scenario 1: Bank Account Block Scam
    test_scenario(
        "Bank Account Block Scam",
        [
            "URGENT! Your bank account will be blocked in 2 hours due to suspicious activity.",
            "We are from State Bank security team. You need to verify your account immediately.",
            "Please provide your account number and registered mobile number for verification.",
            "Also share the OTP we just sent to your phone to confirm your identity.",
            "After verification, we need you to transfer Rs.1 to our security account: 1234567890@paytm"
        ]
    )
    
    # Scenario 2: UPI Fraud
    test_scenario(
        "UPI Fraud",
        [
            "Your UPI transaction of Rs.25,000 has failed. Refund will be processed.",
            "To receive refund, share your UPI PIN to reverse the transaction.",
            "This is urgent. Your money is locked. We need PIN to unlock it.",
            "Send money to test@ybl to verify your UPI is working properly."
        ]
    )
    
    # Scenario 3: Phishing Link Scam
    test_scenario(
        "Phishing Link Scam",
        [
            "Congratulations! You have won Rs.50,000 in our lucky draw.",
            "Click here to claim your prize: http://fake-bank-lottery.com/claim",
            "Enter your bank details on the website to receive the amount.",
            "Hurry! This offer expires in 1 hour."
        ]
    )
    
    # Scenario 4: Tax Refund Scam
    test_scenario(
        "Tax Refund Scam",
        [
            "Income Tax Department: You have a pending refund of Rs.15,000.",
            "To process your refund, we need your PAN card and bank account details.",
            "Call us on +919876543210 or reply with your details.",
            "This is the final notice. Refund will expire after 48 hours."
        ]
    )
    
    # Scenario 5: KYC Update Scam
    test_scenario(
        "KYC Update Scam",
        [
            "Your KYC is incomplete. Account will be suspended if not updated today.",
            "Click this link to update KYC: www.fake-kyc-update.com",
            "Download our app from this link and complete the process.",
            "We need your Aadhaar, PAN, and a selfie holding your card."
        ]
    )
    
    # Scenario 6: Legitimate Message (should not trigger scam detection)
    test_scenario(
        "Legitimate Message",
        [
            "Hi, this is John from work. How are you?",
            "Did you get my email about the project deadline?",
            "Let me know if you need any help.",
            "Thanks!"
        ]
    )
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        All Test Scenarios Completed!                          ║
    ║                                                               ║
    ║  Check the logs to see intelligence extraction and            ║
    ║  final result callbacks sent to GUVI endpoint.               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
