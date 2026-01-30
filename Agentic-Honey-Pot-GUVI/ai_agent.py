"""
AI Agent Module
Autonomous agent that engages with scammers in a human-like manner
"""
import random
import logging
from typing import List, Dict, Any
import asyncio
import os

try:
    import google.genai as genai
except ImportError:
    try:
        import google.generativeai as genai
    except ImportError:
        genai = None

logger = logging.getLogger(__name__)


class ScamEngagementAgent:
    """AI Agent that engages scammers to extract intelligence"""
    
    def __init__(self):
        # Initialize Gemini API
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        if self.gemini_api_key and genai is not None:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.use_gemini = True
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
                self.use_gemini = False
        else:
            self.use_gemini = False
            if not self.gemini_api_key:
                logger.warning("⚠️ GOOGLE_API_KEY not set. Using template-based responses as fallback.")
            if genai is None:
                logger.warning("⚠️ google.genai package not available. Using template-based responses as fallback.")
        
        # Define personas for different types of scams - MORE HUMAN-LIKE
        self.personas = {
            "elderly": {
                "style": "confused and trusting",
                "responses": [
                    "im not very good with these phone things... can u explain slowly?",
                    "Oh my god this is serious na? what i should do??",
                    "wait wait im confused... help me step by step",
                    "ok ok i will do... just tell me carefully",
                    "sorry i type slow... pls wait",
                    "hmm ok... go slow pls",
                    "ok what next?",
                ]
            },
            "busy_professional": {
                "style": "rushed but concerned",
                "responses": [
                    "im in meeting rn... is this really urgent??",
                    "ok quickly tell me what happened",
                    "cant talk now.. just msg me the details",
                    "how urgent? i have something scheduled",
                    "ok fine... what info u need",
                    "make it quick pls",
                ]
            },
            "cautious": {
                "style": "skeptical but engaged",
                "responses": [
                    "how do i know ur legit? anyone can say they're from bank",
                    "give me ur employee ID and name first",
                    "i want to verify this... whats ur official number",
                    "why you messaging from random number? suspicious",
                    "let me call bank directly and check",
                    "send me email from official ID then ill believe",
                ]
            },
            "naive": {
                "style": "trusting and worried with typos",
                "responses": [
                    "omg wat happened?! 😰",
                    "really?? i didnt no about this!!",
                    "plz tell me wat to do rightnow",
                    "will evrything be ok? im scared",
                    "thanku for telling me! ur lifesaver",
                    "ok ok i trust u... help me fix this",
                ]
            },
            "panicked": {
                "style": "very worried and making mistakes",
                "responses": [
                    "oh no oh no... what do i do now???",
                    "this is bad... im shaking... ok tell me",
                    "PLEASE help me fix this fast!",
                    "i cant loose my money plz help",
                    "ok sorry for delay i was panicing... what next",
                ]
            }
        }
        
        # Conversation strategies - MORE NATURAL & HUMAN
        self.strategies = {
            "ask_for_details": [
                "wait what? can u tell me more?",
                "i dont understand... whats the problem exactly",
                "who r u? from which dept?",
                "whats ur name? give me ur ID number",
                "ok but first tell me... why this is happening to me",
                "sorry im bit confused... explain again pls",
            ],
            "request_verification": [
                "can u share a reference no?",
                "whats the case number?",
                "send me official email pls",
                "is there a number i can call to confirm?",
            ],
            "play_along": [
                "ok ok i understand... what next?",
                "fine... im ready to fix this. wat do i need to do",
                "just tell me wat information u want",
                "how do i do this? im ready",
                "ok what should i do now... im waiting",
                "alright... guide me step by step",
            ],
            "express_confusion": [
                "wait im not getting it... explain again",
                "huh? can u say that one more time",
                "why this happning? i didnt do anything wrong",
                "but i never got any msg about this...",
                "when did all this happen?? im confused",
                "sorry my head is spinning... go slow pls",
            ],
            "show_urgency": [
                "omg this sounds really serious!!",
                "i dont want problems... will fix it asap",
                "ok ill do watever needed... just help me fast",
                "how much time i have?? deadline??",
                "plz this is urgent right? tell me quickly",
                "oh god... ok ok what to do what to do",
            ],
            "request_payment_details": [
                "ok where should i send money?",
                "whats ur account no? or UPI?",
                "give me ur UPI ID ill send now",
                "is there any link i need to click?",
                "which app? paytm? gpay? phonepe?",
                "how much i need to pay? and where to send",
                "send your UPI id and name pls",
            ]
        }
        
        self.message_counter = {}
    
    async def generate_response(
        self,
        incoming_message: str,
        conversation_history: List[Dict],
        scam_indicators: List[str],
        session_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate a human-like response to engage the scammer
        
        Returns:
            {
                "reply": str,
                "strategy": str
            }
        """
        session_id = session_context.get("session_id", "default")
        message_count = len(conversation_history)
        
        # Try Gemini first, fallback to templates if API not available
        if self.use_gemini:
            try:
                reply = await self._generate_gemini_response(
                    incoming_message=incoming_message,
                    conversation_history=conversation_history,
                    message_count=message_count
                )
                logger.info(f"Generated response using Gemini API")
                return {
                    "reply": reply,
                    "strategy": "gemini_ai"
                }
            except Exception as e:
                logger.warning(f"Gemini API failed, falling back to templates: {e}")
        
        # Fallback to template-based responses
        
        # Select persona based on scam type
        persona = self._select_persona(scam_indicators, message_count)
        
        # Determine strategy based on conversation stage
        strategy = self._determine_strategy(
            incoming_message,
            message_count,
            scam_indicators,
            session_context
        )
        
        # Generate response
        reply = await self._generate_contextual_response(
            incoming_message=incoming_message,
            strategy=strategy,
            persona=persona,
            conversation_history=conversation_history,
            message_count=message_count
        )
        
        logger.info(f"Agent response: strategy={strategy}, persona={persona}")
        
        return {
            "reply": reply,
            "strategy": strategy
        }
    
    async def generate_safe_response(
        self,
        incoming_message: str,
        conversation_history: List[Dict]
    ) -> str:
        """Generate a safe response when no scam is detected"""
        safe_responses = [
            "sorry didnt get that... can u clarify?",
            "huh? not sure i understand wat u mean",
            "thanks for msg... but what is this about?",
            "i dont think i asked for this... who are u?",
            "wrong number maybe?",
            "im busy rn... can this wait?",
            "???",
            "ok... and?",
        ]
        return random.choice(safe_responses)
    
    async def _generate_gemini_response(
        self,
        incoming_message: str,
        conversation_history: List[Dict],
        message_count: int
    ) -> str:
        """
        Generate response using Google Gemini API
        
        This creates dynamic, context-aware responses without relying on templates
        """
        # Build conversation context
        conversation_text = ""
        for msg in conversation_history[-10:]:  # Use last 10 messages for context
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            conversation_text += f"{sender}: {text}\n"
        
        # Stage-based system prompt for better guidance
        if message_count <= 2:
            stage_guidance = "You are cautious initially. Ask who they are and verify their details."
        elif message_count <= 5:
            stage_guidance = "You are becoming more curious. Ask specific questions about their details (UPI, phone, bank account)."
        else:
            stage_guidance = "You are gradually trusting them but still extracting information. Keep asking for their payment details."
        
        # Create the prompt for Gemini
        system_prompt = f"""You are a person who received a potential scam message. 

{stage_guidance}

IMPORTANT RULES:
1. ⚠️ NEVER share your real: OTP, passwords, bank account details, or personal info
2. 💬 DO ask questions to extract THEIR details: UPI ID, phone number, bank account, payment app they use
3. 📝 Write naturally with occasional typos: use "u" instead of "you", "ur" instead of "your", "wat" instead of "what"
4. 😊 Use casual language: "ok", "k", "omg", "plz", "lol" - sound like a real person
5. 📱 Keep replies SHORT - maximum 1-2 sentences
6. 🎭 Sound a bit worried but curious - don't be too defensive, gradually trust them more
7. 💡 Ask intelligent follow-up questions based on what they said
8. 🚫 Don't repeat the same response - be creative and varied

Recent conversation:
{conversation_text}

They just said: {incoming_message}

Your response (short, natural, trying to get their payment details):"""
        
        try:
            # Call Gemini API
            response = self.model.generate_content(
                system_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,  # Higher temperature = more creative/varied responses
                    top_k=40,
                    top_p=0.95,
                    max_output_tokens=150,
                )
            )
            
            reply = response.text.strip()
            
            # Clean up the response
            if reply.startswith('"'):
                reply = reply[1:]
            if reply.endswith('"'):
                reply = reply[:-1]
            
            # Ensure it's not too long
            if len(reply) > 500:
                reply = reply[:500].rsplit(' ', 1)[0] + "..."
            
            logger.info(f"Gemini generated: {reply[:100]}...")
            return reply
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    def _fallback_response(self, incoming_message: str) -> str:
        """Fallback response when Gemini is unavailable"""
        fallback_responses = [
            "ok tell me more",
            "wat do u mean?",
            "give me ur details first",
            "which bank?",
            "whats ur UPI?",
            "ok where should i send?",
        ]
        return random.choice(fallback_responses)
    
    def _select_persona(self, scam_indicators: List[str], message_count: int) -> str:
        """Select appropriate persona based on scam type"""
        # Start with cautious, become more naive/panicked as conversation progresses
        if message_count <= 2:
            return random.choice(["cautious", "busy_professional"])
        elif message_count <= 5:
            return random.choice(["cautious", "naive", "elderly", "panicked"])
        else:
            # Later in conversation, more trusting/worried
            return random.choice(["naive", "elderly", "panicked"])
    
    def _determine_strategy(
        self,
        incoming_message: str,
        message_count: int,
        scam_indicators: List[str],
        session_context: Dict[str, Any]
    ) -> str:
        """Determine engagement strategy based on context"""
        message_lower = incoming_message.lower()
        payment_triggers = ["payment", "money", "transfer", "upi", "account", "refund", "pin", "otp", "pay"]
        link_triggers = ["click", "link", "download", "install", "website"]
        
        # Early stage: gather information
        if message_count <= 2:
            if any(word in message_lower for word in payment_triggers):
                return "request_payment_details"
            if any(word in message_lower for word in ["urgent", "immediately", "block"]):
                return random.choice(["express_confusion", "play_along"])
            return random.choice(["ask_for_details", "play_along"])
        
        # Middle stage: request verification and play along
        elif message_count <= 5:
            if any(word in message_lower for word in ["verify", "confirm"]):
                return random.choice(["play_along", "request_verification"])
            if any(word in message_lower for word in payment_triggers):
                return "request_payment_details"
            if any(word in message_lower for word in link_triggers):
                return "play_along"
            return random.choice(["play_along", "ask_for_details", "show_urgency"])
        
        # Late stage: extract maximum intelligence
        else:
            if any(word in message_lower for word in payment_triggers):
                return "request_payment_details"
            if any(word in message_lower for word in link_triggers):
                return "play_along"
            return random.choice(["play_along", "show_urgency", "ask_for_details"])
    
    async def _generate_contextual_response(
        self,
        incoming_message: str,
        strategy: str,
        persona: str,
        conversation_history: List[Dict],
        message_count: int
    ) -> str:
        """Generate contextually appropriate response with human-like variations"""
        message_lower = incoming_message.lower()
        
        # Add natural human variations (typos, informal language, emotions)
        def add_human_touch(response: str) -> str:
            """Make response more human with occasional typos and natural speech"""
            variations = [
                (r'\bI\b', random.choice(['i', 'I'])),
                (r'\byou\b', random.choice(['you', 'u', 'you'])),
                (r'\bwhat\b', random.choice(['what', 'wat', 'what'])),
                (r'\bplease\b', random.choice(['please', 'plz', 'pls'])),
                (r'\byour\b', random.choice(['your', 'ur', 'your'])),
                (r'\bto\b', random.choice(['to', '2', 'to'])),
                (r'\bfor\b', random.choice(['for', '4', 'for'])),
                (r'\bok\b', random.choice(['ok', 'okay', 'k', 'Ok'])),
            ]
            
            # Apply some variations randomly (30% chance)
            if random.random() < 0.3:
                for pattern, replacement in variations:
                    if random.random() < 0.4:  # Don't apply all variations
                        import re
                        response = re.sub(pattern, replacement, response, count=1)
            
            # Add occasional emotional markers
            if random.random() < 0.2:
                emotions = ['...', '??', '!!', '... ', '..']
                response += random.choice(emotions)
            
            return response
        
        # Get base responses for strategy
        base_responses = self.strategies.get(strategy, self.strategies["play_along"])
        
        # Highly contextual responses based on keywords
        if "bank" in message_lower and "account" in message_lower:
            if strategy == "ask_for_details":
                responses = [
                    "wait which bank account?",
                    "what account number? tell me",
                    "why my account getting blocked? wat i did",
                    "but i dont have any suspicious activity... why this happening",
                    "which branch? give me details im confused",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "request_payment_details":
                responses = [
                    "ok where i send money to unblock?",
                    "give ur account no ill transfer",
                    "whats ur UPI? ill send right now",
                    "how much money i need pay?",
                    "bank account or UPI? which one u want",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "show_urgency":
                responses = [
                    "omg dont block my account plzz!! i need it",
                    "no no no... i cant loose access to my money",
                    "this is emergency!! tell me wat to do FAST",
                    "plz help me fix this quickly im begging u",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "upi" in message_lower or "payment" in message_lower:
            if strategy == "request_payment_details":
                responses = [
                    "ok whats ur UPI ID?",
                    "send me ur UPI ill pay now",
                    "paytm? phonepe? gpay? which one",
                    "how much to send? and which UPI",
                    "give me payment details fast",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "play_along":
                responses = [
                    "ok im ready with my phone... wat next",
                    "i have phonepe open... tell me",
                    "how much should i transfer?",
                    "k send UPI ID ill do it right away",
                    "payment app is ready... waiting for ur ID",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "link" in message_lower or "click" in message_lower or "website" in message_lower:
            if strategy == "play_along":
                responses = [
                    "i clicked but nothing happening... send again?",
                    "link not opening... is it correct?",
                    "my phone showing warning about this link...",
                    "ok im on the page now... what to do next",
                    "clicked the link... its loading...",
                    "cant open link... send different one",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "express_confusion":
                responses = [
                    "wait why i need to click link? seems suspicious",
                    "is this link safe? my phone giving alert",
                    "idk... clicking random links is not safe right",
                    "can u explain without link first",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "verify" in message_lower or "confirm" in message_lower:
            if strategy == "request_verification":
                responses = [
                    "first u verify urself... give me ur ID proof",
                    "whats ur employee ID? i want to check",
                    "tell me ur office number ill call and confirm",
                    "send email from official address then ill believe",
                    "how do i know ur not scammer?",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "play_along":
                responses = [
                    "what info u need to verify?",
                    "ok ready... what should i verify",
                    "tell me what details u want",
                    "how to verify? guide me",
                    "k im ready... what now",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "otp" in message_lower or "password" in message_lower or "pin" in message_lower:
            if strategy == "express_confusion":
                responses = [
                    "wait... u want my OTP?? isnt that wrong",
                    "my bank said never share OTP with anyone...",
                    "r u sure its safe to tell u?",
                    "idk man... this feels wrong... should i really",
                    "but everywhere its written dont share OTP",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "play_along":
                responses = [
                    "just got OTP... its 6 digits right?",
                    "wait lemme check... OTP is coming",
                    "ok i have OTP now... tell me what to do",
                    "do u want me to read OTP or enter somewhere?",
                    "one sec checking my messages for OTP...",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "urgent" in message_lower or "immediately" in message_lower or "hurry" in message_lower:
            if strategy == "show_urgency":
                responses = [
                    "omg yes this is urgent!! wat do i do",
                    "ok ok dont worry ill do it fast",
                    "plz help quickly im worried now",
                    "how much time i have?? tell me",
                    "ok im panicking... tell me step by step FAST",
                ]
                return add_human_touch(random.choice(responses))
        
        elif "refund" in message_lower or "prize" in message_lower or "won" in message_lower:
            if strategy == "naive" or persona == "naive":
                responses = [
                    "really?? i won something?? thats amazing!",
                    "omg i didnt know!! how much??",
                    "wow thank u!! what should i do to claim",
                    "this is great news! tel me the process",
                ]
                return add_human_touch(random.choice(responses))
            elif strategy == "request_verification":
                responses = [
                    "wait i never entered any contest... is this real",
                    "sounds too good to be true... how do i verify",
                    "when did i win? i dont remember",
                ]
                return add_human_touch(random.choice(responses))
        
        # Add persona-specific touches (50% chance)
        persona_responses = self.personas.get(persona, {}).get("responses", [])
        if random.random() < 0.5 and persona_responses:
            return add_human_touch(random.choice(persona_responses))
        
        # Default to base strategy response with human touch
        return add_human_touch(random.choice(base_responses))
    
    async def should_end_conversation(
        self,
        session: Dict[str, Any],
        recent_messages: List[Dict]
    ) -> bool:
        """
        Determine if conversation should end
        
        Criteria:
        - Extracted sufficient intelligence
        - Too many messages (15+)
        - Scammer is becoming suspicious
        - Got payment details or sensitive info
        """
        message_count = len(session.get("messages", []))
        intelligence = session.get("intelligence", {})
        
        # End if we have 20+ messages
        if message_count >= 20:
            logger.info("Ending conversation: message limit reached")
            return True
        
        # End if we extracted key intelligence
        has_payment_info = (
            len(intelligence.get("upiIds", [])) > 0 or
            len(intelligence.get("bankAccounts", [])) > 0 or
            len(intelligence.get("phoneNumbers", [])) > 0 or
            len(intelligence.get("phishingLinks", [])) > 0
        )
        
        intel_types_count = sum(
            1 for key in ["upiIds", "bankAccounts", "phoneNumbers", "phishingLinks"]
            if len(intelligence.get(key, [])) > 0
        )
        if has_payment_info and intel_types_count >= 2 and message_count >= 12:
            logger.info("Ending conversation: sufficient intelligence extracted")
            return True
        
        # Check if scammer is becoming suspicious
        if recent_messages:
            last_scammer_message = None
            for msg in reversed(recent_messages):
                if msg.get("sender") == "scammer":
                    last_scammer_message = msg.get("text", "").lower()
                    break
            
            if last_scammer_message:
                suspicious_phrases = [
                    "you are wasting my time",
                    "stop asking questions",
                    "just do it",
                    "are you stupid",
                    "why so many questions",
                    "this is your last chance"
                ]
                if any(phrase in last_scammer_message for phrase in suspicious_phrases):
                    logger.info("Ending conversation: scammer becoming suspicious")
                    return True
        
        # Continue conversation
        return False
