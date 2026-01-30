"""
Debug script to test intelligence extraction directly
"""
import asyncio
import re

# Test the patterns directly
patterns = {
    "upi": r'[\w\.\-]+@[\w\.]+'  ,
    "phone": r'(?:\+91|0)?[\s\-\.]?[6-9]\d{1}[\s\-\.]?\d{4}[\s\-\.]?\d{4}|\+\d{1,3}[\s\.\-]?\d{6,14}',
    "url": r'https?://[^\s]+|www\.[^\s]+|[a-z0-9\-]+\.[a-z]{2,}(?:/[^\s]*)?',
}

test_texts = [
    "After verification, we need you to transfer Rs.1 to our security account: 1234567890@paytm",
    "Call us on +919876543210 or reply with your details.",
    "Click here to claim your prize: http://fake-bank-lottery.com/claim",
    "Click this link to update KYC: www.fake-kyc-update.com",
    "Send money to test@ybl to verify your UPI is working properly.",
]

print("Testing intelligence extraction patterns:\n")

for text in test_texts:
    print(f"Text: {text}")
    
    # Test UPI
    upi_matches = re.findall(patterns["upi"], text, re.IGNORECASE)
    print(f"  UPI matches: {upi_matches}")
    
    # Test Phone
    phone_matches = re.findall(patterns["phone"], text)
    print(f"  Phone matches: {phone_matches}")
    
    # Test URL
    url_matches = re.findall(patterns["url"], text, re.IGNORECASE)
    print(f"  URL matches: {url_matches}")
    
    print()
