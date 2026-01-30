"""
Full integration test for intelligence extraction
"""
import asyncio
import sys
sys.path.insert(0, 'C:\\Users\\rahul\\OneDrive\\Desktop\\2nd Year\\GUVI\\Agentic-Honey-Pot-GUVI')

from intelligence_extractor import IntelligenceExtractor

async def test_extraction():
    extractor = IntelligenceExtractor()
    
    conversation = [
        {"sender": "scammer", "text": "URGENT! Your bank account will be blocked in 2 hours.", "timestamp": "2026-01-30T21:00:00Z"},
        {"sender": "scammer", "text": "We are from State Bank security team. You need to verify your account immediately.", "timestamp": "2026-01-30T21:00:10Z"},
        {"sender": "scammer", "text": "Please provide your account number and registered mobile number for verification.", "timestamp": "2026-01-30T21:00:20Z"},
        {"sender": "scammer", "text": "Also share the OTP we just sent to your phone to confirm your identity.", "timestamp": "2026-01-30T21:00:30Z"},
        {"sender": "scammer", "text": "After verification, we need you to transfer Rs.1 to our security account: 1234567890@paytm", "timestamp": "2026-01-30T21:00:40Z"},
    ]
    
    latest_message = "After verification, we need you to transfer Rs.1 to our security account: 1234567890@paytm"
    
    print("Testing Intelligence Extraction")
    print("=" * 60)
    print(f"Conversation messages: {len(conversation)}")
    print(f"Latest message: {latest_message}\n")
    
    intelligence = await extractor.extract(
        conversation=conversation,
        latest_message=latest_message
    )
    
    print("Extracted Intelligence:")
    print("-" * 60)
    for key, values in intelligence.items():
        print(f"{key}: {len(values) if isinstance(values, list) else 1} items")
        if isinstance(values, list) and values:
            for v in values:
                print(f"  - {v}")
    
asyncio.run(test_extraction())
