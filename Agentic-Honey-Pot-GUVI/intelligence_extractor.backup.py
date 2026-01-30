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
            # UPI IDs: something@bank (improved pattern)
            "upi": r'[\w\.\-]+@[\w\.]+',
            
            # Phone numbers: Indian format primarily +91 or 0, then 9-10 digits
            "phone": r'(?:\+91|0)?[\s\-\.]?[6-9]\d{1}[\s\-\.]?\d{4}[\s\-\.]?\d{4}|\+\d{1,3}[\s\.\-]?\d{6,14}',
            
            # Bank account numbers: 9-18 digits (but be careful not to match regular numbers)
            "account": r'\b\d{9,18}\b',
            
            # URLs and links (improved)
            "url": r'https?://[^\s]+|www\.[^\s]+|[a-z0-9\-]+\.[a-z]{2,}(?:/[^\s]*)?',
            
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
        
            # Extract additional context-specific intelligence (only keywords)
            contextual_intel = self._extract_contextual_intelligence(all_text)
            # Only merge the suspiciousKeywords, don't overwrite other keys
            intelligence["suspiciousKeywords"].extend(contextual_intel["suspiciousKeywords"])
        
        # Remove duplicates
        for key in intelligence:
            if isinstance(intelligence[key], list):
                intelligence[key] = list(set(intelligence[key]))
        
        logger.info(f"Extracted intelligence: {intelligence}")
        
        return intelligence
    
    def _clean_and_validate_upi(self, upi_matches: List[str]) -> List[str]:
        """Clean and validate UPI IDs"""
        valid_upis = []
        seen = set()
        
        logger.debug(f"UPI validation - Input matches: {upi_matches}")
        
        for upi in upi_matches:
            upi = upi.strip().lower()
            logger.debug(f"Processing UPI: {upi}")
            
            # Check if it looks like a valid UPI
            if '@' not in upi or len(upi) < 5:
                logger.debug(f"  Rejected: Missing @ or too short")
                continue
            
            # Common UPI providers
            valid_providers = ['paytm', 'phonepe', 'googlepay', 'ybl', 'okaxis', 
                             'oksbi', 'okicici', 'okhdfc', 'upi', 'apl', 'axl', 'ibl', 'barodampay']
            
            provider = upi.split('@')[-1]
            logger.debug(f"  Provider: {provider}")
            
            # Accept if provider matches known ones OR if it's a plausible domain
            matches_provider = any(p in provider for p in valid_providers)
            has_domain = len(provider) > 2 and '.' in provider
            logger.debug(f"  Matches provider: {matches_provider}, Has domain: {has_domain}")
            
            if matches_provider or has_domain:
                if upi not in seen:
                    logger.debug(f"  ADDED: {upi}")
                    valid_upis.append(upi)
                    seen.add(upi)
                else:
                    logger.debug(f"  Duplicate: {upi}")
            else:
                logger.debug(f"  Rejected: Provider not recognized")
        
        logger.debug(f"UPI validation - Output: {valid_upis}")
        return valid_upis
    
    def _clean_and_validate_phones(self, phone_matches: List[str]) -> List[str]:
        """Clean and validate phone numbers"""
        valid_phones = []
        seen = set()
        
        for phone in phone_matches:
            if not phone:
                continue
                
            # Remove non-digits for validation
            digits = re.sub(r'\D', '', phone)
            
            # Valid phone numbers are 10-15 digits
            if 10 <= len(digits) <= 15:
                # Format nicely for Indian numbers
                if len(digits) == 10:
                    formatted = f"+91{digits}"
                elif len(digits) == 11 and digits.startswith('0'):
                    formatted = f"+91{digits[1:]}"
                elif len(digits) == 12 and digits.startswith('91'):
                    formatted = f"+{digits}"
                else:
                    formatted = f"+{digits}"
                
                if formatted not in seen:
                    valid_phones.append(formatted)
                    seen.add(formatted)
        
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
        seen = set()
        
        for url in url_matches:
            if not url:
                continue
                
            url = url.strip()
            # Remove trailing punctuation
            url = re.sub(r'[.,;!?\'\")\]]+$', '', url)
            
            # Add http if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'http://' + url
                else:
                    url = 'http://' + url
            
            # Check if it looks like a valid URL
            if '.' in url and len(url) > 7:
                if url not in seen:
                    valid_urls.append(url)
                    seen.add(url)
        
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
