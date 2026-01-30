"""
Scam Detector Module
Uses AI to detect scam intent in messages
"""
import re
import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class ScamDetector:
    """Detects scam intent using pattern matching and AI analysis"""
    
    def __init__(self):
        # Common scam indicators
        self.urgency_keywords = [
            "urgent", "immediately", "right now", "expire", "expires", "expired",
            "today only", "limited time", "act now", "hurry", "quick", "deadline",
            "suspend", "suspended", "blocked", "block", "freeze", "frozen"
        ]
        
        self.threat_keywords = [
            "account blocked", "account suspended", "legal action", "arrest",
            "police", "law enforcement", "penalty", "fine", "criminal",
            "lawsuit", "court", "jail", "prison", "warrant"
        ]
        
        self.request_keywords = [
            "verify", "confirm", "update", "share", "send", "provide",
            "click here", "link", "download", "install", "open attachment",
            "enter password", "enter pin", "enter otp", "card details",
            "cvv", "expire date"
        ]
        
        self.financial_keywords = [
            "bank account", "credit card", "debit card", "upi", "paytm",
            "phone pe", "google pay", "net banking", "ifsc", "account number",
            "cvv", "pin", "password", "otp", "transfer money", "refund",
            "cashback", "reward", "prize", "won", "lottery", "winner"
        ]
        
        self.impersonation_keywords = [
            "we are from", "calling from", "representative", "customer care",
            "support team", "security team", "fraud department", "bank official",
            "government", "tax department", "income tax", "rbi", "sebi"
        ]
        
        # Regex patterns for sensitive data
        self.patterns = {
            "phone": r'\+?[\d\s\-\(\)]{10,}',
            "upi": r'[\w\.\-]+@[\w]+',
            "url": r'https?://[^\s]+|www\.[^\s]+',
            "account": r'\b\d{9,18}\b',
            "amount": r'₹[\d,]+|Rs\.?\s*[\d,]+|\$[\d,]+'
        }
    
    async def analyze(
        self,
        message: str,
        conversation_history: List[str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze message for scam indicators
        
        Returns:
            {
                "is_scam": bool,
                "confidence": float,
                "indicators": List[str],
                "notes": str
            }
        """
        message_lower = message.lower()
        indicators = []
        confidence_score = 0.0
        
        # Check for urgency
        urgency_count = sum(1 for keyword in self.urgency_keywords if keyword in message_lower)
        if urgency_count > 0:
            indicators.append("urgency_tactics")
            confidence_score += min(urgency_count * 0.15, 0.3)
        
        # Check for threats
        threat_count = sum(1 for keyword in self.threat_keywords if keyword in message_lower)
        if threat_count > 0:
            indicators.append("threatening_language")
            confidence_score += min(threat_count * 0.2, 0.4)
        
        # Check for suspicious requests
        request_count = sum(1 for keyword in self.request_keywords if keyword in message_lower)
        if request_count > 0:
            indicators.append("suspicious_requests")
            confidence_score += min(request_count * 0.1, 0.25)
        
        # Check for financial keywords
        financial_count = sum(1 for keyword in self.financial_keywords if keyword in message_lower)
        if financial_count > 0:
            indicators.append("financial_focus")
            confidence_score += min(financial_count * 0.12, 0.3)
        
        # Check for impersonation
        impersonation_count = sum(1 for keyword in self.impersonation_keywords if keyword in message_lower)
        if impersonation_count > 0:
            indicators.append("impersonation_attempt")
            confidence_score += min(impersonation_count * 0.15, 0.35)
        
        # Check for URLs (phishing links)
        if re.search(self.patterns["url"], message):
            indicators.append("contains_links")
            confidence_score += 0.25
        
        # Check for sensitive data requests
        sensitive_patterns = ["otp", "cvv", "pin", "password", "card number"]
        if any(pattern in message_lower for pattern in sensitive_patterns):
            indicators.append("requests_sensitive_data")
            confidence_score += 0.35
        
        # Contextual analysis
        if len(conversation_history) == 0:
            # First message - check for cold approach
            if any(phrase in message_lower for phrase in ["we are from", "calling from", "this is"]):
                indicators.append("unsolicited_contact")
                confidence_score += 0.2
        
        # Grammar and spelling (scammers often have poor grammar)
        if self._has_poor_grammar(message):
            indicators.append("poor_grammar")
            confidence_score += 0.1
        
        # Cap confidence at 1.0
        confidence_score = min(confidence_score, 1.0)
        
        # Determine if it's a scam
        is_scam = confidence_score >= 0.5 or len(indicators) >= 3
        
        # Generate notes
        notes = self._generate_notes(indicators, confidence_score)
        
        logger.info(f"Scam analysis: is_scam={is_scam}, confidence={confidence_score:.2f}, indicators={indicators}")
        
        return {
            "is_scam": is_scam,
            "confidence": round(confidence_score, 2),
            "indicators": indicators,
            "notes": notes
        }
    
    def _has_poor_grammar(self, message: str) -> bool:
        """Check for signs of poor grammar"""
        # Multiple punctuation
        if re.search(r'[!?]{2,}', message):
            return True
        
        # All caps (shouting)
        if len(message) > 10 and message.isupper():
            return True
        
        # Random capitalization
        words = message.split()
        if len(words) > 5:
            capitalized = sum(1 for word in words if word and word[0].isupper())
            if capitalized > len(words) * 0.7:  # More than 70% capitalized
                return True
        
        return False
    
    def _generate_notes(self, indicators: List[str], confidence: float) -> str:
        """Generate human-readable notes about the detection"""
        if not indicators:
            return "No significant scam indicators detected"
        
        notes_parts = []
        
        if "urgency_tactics" in indicators:
            notes_parts.append("Uses urgency to pressure victim")
        if "threatening_language" in indicators:
            notes_parts.append("Employs threats or intimidation")
        if "suspicious_requests" in indicators:
            notes_parts.append("Requests sensitive actions")
        if "financial_focus" in indicators:
            notes_parts.append("Focuses on financial information")
        if "impersonation_attempt" in indicators:
            notes_parts.append("Attempts to impersonate authority")
        if "contains_links" in indicators:
            notes_parts.append("Contains potentially malicious links")
        if "requests_sensitive_data" in indicators:
            notes_parts.append("Directly requests sensitive data (OTP/PIN/CVV)")
        if "unsolicited_contact" in indicators:
            notes_parts.append("Unsolicited contact from unknown source")
        if "poor_grammar" in indicators:
            notes_parts.append("Exhibits poor grammar/formatting")
        
        return "; ".join(notes_parts)
