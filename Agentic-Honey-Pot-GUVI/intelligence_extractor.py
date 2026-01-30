"""
Intelligence Extractor Module
Extracts actionable intelligence from scam conversations
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """Extracts scam-related intelligence from conversations"""
    
    def __init__(self):
        # Regex patterns for various types of intelligence
        self.patterns = {
            # UPI IDs: something@bank
            "upi": r'\b[\w\.\-]+@[\w]+\b',
            
            # Phone numbers: various formats
            "phone": r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            
            # Bank account numbers: 9-18 digits
            "account": r'\b\d{9,18}\b',
            
            # URLs and links
            "url": r'https?://[^\s]+|www\.[^\s]+|[a-z0-9\-]+\.[a-z]{2,}[^\s]*',
            
            # IFSC codes
            "ifsc": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            
            # Amounts
            "amount": r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{2})?|\b\d+\s*(?:rupees|rs|inr)\b'
        }
        
        # Suspicious keywords to track
        self.suspicious_keywords = [
            "urgent", "immediate", "verify", "confirm", "blocked", "suspended",
            "expire", "deadline", "penalty", "fine", "arrest", "legal action",
            "click here", "download", "install", "otp", "cvv", "pin",
            "password", "account number", "card details", "transfer money",
            "refund", "cashback", "prize", "lottery", "winner", "reward",
            "tax refund", "government", "bank official", "customer care"
        ]
    
    async def extract(
        self,
        conversation: List[Dict],
        latest_message: str
    ) -> Dict[str, List[str]]:
        """
        Extract intelligence from conversation
        
        Returns:
            {
                "bankAccounts": [...],
                "upiIds": [...],
                "phishingLinks": [...],
                "phoneNumbers": [...],
                "suspiciousKeywords": [...]
            }
        """
        intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        # Combine all messages for analysis
        all_text = " ".join([msg.get("text", "") for msg in conversation if msg.get("sender") == "scammer"])
        all_text += " " + latest_message
        
        # Extract UPI IDs
        upi_matches = re.findall(self.patterns["upi"], all_text, re.IGNORECASE)
        intelligence["upiIds"] = self._clean_and_validate_upi(upi_matches)
        
        # Extract phone numbers
        phone_matches = re.findall(self.patterns["phone"], all_text)
        intelligence["phoneNumbers"] = self._clean_and_validate_phones(phone_matches)
        
        # Extract bank accounts
        account_matches = re.findall(self.patterns["account"], all_text)
        intelligence["bankAccounts"] = self._clean_and_validate_accounts(account_matches)
        
        # Extract URLs
        url_matches = re.findall(self.patterns["url"], all_text, re.IGNORECASE)
        intelligence["phishingLinks"] = self._clean_and_validate_urls(url_matches)
        
        # Extract IFSC codes (add to bank accounts with IFSC: prefix)
        ifsc_matches = re.findall(self.patterns["ifsc"], all_text)
        for ifsc in ifsc_matches:
            intelligence["bankAccounts"].append(f"IFSC:{ifsc}")
        
        # Extract suspicious keywords
        text_lower = all_text.lower()
        found_keywords = [kw for kw in self.suspicious_keywords if kw in text_lower]
        intelligence["suspiciousKeywords"] = list(set(found_keywords))
        
        # Extract additional context-specific intelligence
        intelligence.update(self._extract_contextual_intelligence(all_text))
        
        # Remove duplicates
        for key in intelligence:
            if isinstance(intelligence[key], list):
                intelligence[key] = list(set(intelligence[key]))
        
        logger.info(f"Extracted intelligence: {intelligence}")
        
        return intelligence
    
    def _clean_and_validate_upi(self, upi_matches: List[str]) -> List[str]:
        """Clean and validate UPI IDs"""
        valid_upis = []
        for upi in upi_matches:
            upi = upi.strip()
            # Check if it looks like a valid UPI
            if '@' in upi and len(upi) > 5:
                # Common UPI providers
                valid_providers = ['paytm', 'phonepe', 'googlepay', 'ybl', 'okaxis', 
                                 'oksbi', 'okicici', 'okhdfc', 'upi', 'apl', 'axl']
                provider = upi.split('@')[-1].lower()
                if any(p in provider for p in valid_providers) or len(provider) <= 10:
                    valid_upis.append(upi)
        return valid_upis
    
    def _clean_and_validate_phones(self, phone_matches: List[str]) -> List[str]:
        """Clean and validate phone numbers"""
        valid_phones = []
        for phone in phone_matches:
            # Remove non-digits
            digits = re.sub(r'\D', '', phone)
            # Valid phone numbers are 10-15 digits
            if 10 <= len(digits) <= 15:
                # Format nicely
                if digits.startswith('91') and len(digits) == 12:
                    formatted = f"+91{digits[2:]}"
                elif digits.startswith('0') and len(digits) == 11:
                    formatted = f"+91{digits[1:]}"
                elif len(digits) == 10:
                    formatted = f"+91{digits}"
                else:
                    formatted = f"+{digits}"
                valid_phones.append(formatted)
        return valid_phones
    
    def _clean_and_validate_accounts(self, account_matches: List[str]) -> List[str]:
        """Clean and validate bank account numbers"""
        valid_accounts = []
        for account in account_matches:
            # Remove spaces and special chars
            clean = re.sub(r'\D', '', account)
            # Valid account numbers are 9-18 digits
            if 9 <= len(clean) <= 18:
                # Mask for privacy (show first 4 and last 4)
                if len(clean) > 8:
                    masked = f"{clean[:4]}{'*' * (len(clean) - 8)}{clean[-4:]}"
                else:
                    masked = f"{clean[:4]}{'*' * (len(clean) - 4)}"
                valid_accounts.append(masked)
        return valid_accounts
    
    def _clean_and_validate_urls(self, url_matches: List[str]) -> List[str]:
        """Clean and validate URLs"""
        valid_urls = []
        for url in url_matches:
            url = url.strip()
            # Remove trailing punctuation
            url = re.sub(r'[.,;!?]+$', '', url)
            
            # Add http if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'http://' + url
                else:
                    url = 'http://' + url
            
            # Check if it looks like a valid URL
            if '.' in url and len(url) > 5:
                valid_urls.append(url)
        return valid_urls
    
    def _extract_contextual_intelligence(self, text: str) -> Dict[str, List[str]]:
        """Extract additional contextual intelligence"""
        additional_intel = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        text_lower = text.lower()
        
        # Look for specific scam patterns
        
        # Tax refund scam
        if any(word in text_lower for word in ["tax refund", "income tax", "refund pending"]):
            additional_intel["suspiciousKeywords"].extend(["tax_refund_scam", "government_impersonation"])
        
        # Prize/lottery scam
        if any(word in text_lower for word in ["won prize", "lottery", "winner", "congratulations"]):
            additional_intel["suspiciousKeywords"].extend(["lottery_scam", "prize_scam"])
        
        # Bank account block scam
        if any(word in text_lower for word in ["account blocked", "account suspended", "kyc pending"]):
            additional_intel["suspiciousKeywords"].extend(["account_block_scam", "bank_impersonation"])
        
        # OTP scam
        if any(word in text_lower for word in ["share otp", "tell otp", "send otp"]):
            additional_intel["suspiciousKeywords"].extend(["otp_fraud", "credential_theft"])
        
        # Phishing link scam
        if any(word in text_lower for word in ["click link", "open link", "visit website"]):
            additional_intel["suspiciousKeywords"].extend(["phishing_attempt", "malicious_link"])
        
        # Payment redirection scam
        if any(word in text_lower for word in ["transfer to", "send money to", "pay to"]):
            additional_intel["suspiciousKeywords"].extend(["payment_redirection", "money_transfer_scam"])
        
        # Extract payment apps mentioned
        payment_apps = ["paytm", "phonepe", "google pay", "gpay", "bhim", "whatsapp pay"]
        mentioned_apps = [app for app in payment_apps if app in text_lower]
        if mentioned_apps:
            additional_intel["suspiciousKeywords"].extend([f"uses_{app.replace(' ', '_')}" for app in mentioned_apps])
        
        # Extract impersonation targets
        impersonation_targets = [
            "bank", "police", "income tax", "government", "customer care",
            "security team", "fraud department", "cyber cell"
        ]
        mentioned_targets = [target for target in impersonation_targets if target in text_lower]
        if mentioned_targets:
            additional_intel["suspiciousKeywords"].extend([f"impersonates_{target.replace(' ', '_')}" for target in mentioned_targets])
        
        return additional_intel
