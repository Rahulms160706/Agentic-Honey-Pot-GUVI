"""
Agentic Honey-Pot for Scam Detection & Intelligence Extraction
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, Security, Header
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uvicorn
import logging
import asyncio
import requests
from scam_detector import ScamDetector
from ai_agent import ScamEngagementAgent
from intelligence_extractor import IntelligenceExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# API Key configuration
API_KEY = os.getenv("API_KEY", "YOUR_SECRET_API_KEY_12345")  # Change this to a secure key
api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)

# GUVI callback endpoint
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Initialize components
scam_detector = ScamDetector()
ai_agent = ScamEngagementAgent()
intelligence_extractor = IntelligenceExtractor()

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class Message(BaseModel):
    sender: str = Field(..., description="'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class Metadata(BaseModel):
    channel: Optional[str] = Field(None, description="SMS/WhatsApp/Email/Chat")
    language: Optional[str] = Field(None, description="Language used")
    locale: Optional[str] = Field(None, description="Country or region")


class IncomingMessageRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: List[Message] = Field(default_factory=list, description="Previous messages")
    metadata: Optional[Metadata] = Field(None, description="Additional context")


class AgentResponse(BaseModel):
    status: str = Field(..., description="success or error")
    reply: str = Field(..., description="Agent's response to the scammer")
    scamDetected: Optional[bool] = Field(None, description="Whether scam was detected")
    confidenceScore: Optional[float] = Field(None, description="Confidence in scam detection")


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class FinalResultPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


def verify_api_key(x_api_key: str = Security(api_key_header)):
    """Verify API key"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


def send_final_result_callback(payload: FinalResultPayload):
    """Send final result to GUVI evaluation endpoint"""
    try:
        logger.info(f"Sending final result for session {payload.sessionId}")
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload.dict(),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Successfully sent final result: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send final result: {str(e)}")
        return False


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Agentic Honey-Pot API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "scam_detector": "operational",
            "ai_agent": "operational",
            "intelligence_extractor": "operational"
        }
    }


@app.post("/api/message", response_model=AgentResponse)
async def handle_message(
    request: IncomingMessageRequest,
    api_key: str = Security(verify_api_key)
):
    """
    Main endpoint for handling incoming messages
    Detects scams, engages with AI agent, and extracts intelligence
    """
    try:
        session_id = request.sessionId
        incoming_message = request.message
        conversation_history = request.conversationHistory
        metadata = request.metadata
        
        logger.info(f"Processing message for session {session_id}")
        
        # Initialize or retrieve session
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "scam_detected": False,
                "confidence_score": 0.0,
                "intelligence": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "suspiciousKeywords": []
                },
                "agent_notes": [],
                "created_at": datetime.utcnow().isoformat()
            }
        
        session = sessions[session_id]
        
        # Add incoming message to session
        session["messages"].append(incoming_message.dict())
        
        # Build full conversation context (dicts for downstream extractors)
        all_messages = [msg.dict() for msg in conversation_history] + [incoming_message.dict()]
        
        # Step 1: Detect scam intent
        scam_result = await scam_detector.analyze(
            message=incoming_message.text,
            conversation_history=[msg.text for msg in conversation_history],
            metadata=metadata.dict() if metadata else {}
        )
        
        session["scam_detected"] = scam_result["is_scam"]
        session["confidence_score"] = scam_result["confidence"]
        
        logger.info(f"Scam detection: {scam_result['is_scam']} (confidence: {scam_result['confidence']})")
        
        # Extract intelligence from EVERY message (regardless of scam detection)
        extracted_intel = await intelligence_extractor.extract(
            conversation=all_messages,
            latest_message=incoming_message.text
        )
        
        # Update session intelligence
        for key in extracted_intel:
            if key in session["intelligence"]:
                session["intelligence"][key].extend(extracted_intel[key])
                # Remove duplicates
                session["intelligence"][key] = list(set(session["intelligence"][key]))
        
        logger.info(f"Intelligence extracted: UPIs={len(session['intelligence']['upiIds'])}, "
                   f"Phones={len(session['intelligence']['phoneNumbers'])}, "
                   f"Links={len(session['intelligence']['phishingLinks'])}")
        
        # Step 2: If scam detected, activate AI agent
        if scam_result["is_scam"]:
            # Generate agent response
            agent_response = await ai_agent.generate_response(
                incoming_message=incoming_message.text,
                conversation_history=all_messages,
                scam_indicators=scam_result["indicators"],
                session_context=session
            )
            
            # Add agent notes
            if scam_result.get("notes"):
                session["agent_notes"].append(scam_result["notes"])
            
            # Store agent's response
            session["messages"].append({
                "sender": "user",
                "text": agent_response["reply"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Step 3: Check if conversation should end and send final result
            should_end = await ai_agent.should_end_conversation(
                session=session,
                recent_messages=all_messages[-5:]  # Last 5 messages
            )
            
            if should_end:
                logger.info(f"Ending conversation for session {session_id}")
                
                # Prepare final result
                final_payload = FinalResultPayload(
                    sessionId=session_id,
                    scamDetected=True,
                    totalMessagesExchanged=len(session["messages"]),
                    extractedIntelligence=ExtractedIntelligence(**session["intelligence"]),
                    agentNotes=" | ".join(session["agent_notes"]) if session["agent_notes"] else "Scam engagement completed successfully"
                )
                
                # Send to GUVI endpoint
                asyncio.create_task(asyncio.to_thread(send_final_result_callback, final_payload))
            
            return AgentResponse(
                status="success",
                reply=agent_response["reply"],
                scamDetected=True,
                confidenceScore=scam_result["confidence"]
            )
        else:
            # No scam detected - respond naturally but cautiously
            safe_response = await ai_agent.generate_safe_response(
                incoming_message=incoming_message.text,
                conversation_history=all_messages
            )
            
            return AgentResponse(
                status="success",
                reply=safe_response,
                scamDetected=False,
                confidenceScore=scam_result["confidence"]
            )
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(
    session_id: str,
    api_key: str = Security(verify_api_key)
):
    """Get session details (for debugging/monitoring)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session_id,
        "session": sessions[session_id]
    }


@app.get("/api/intelligence/{session_id}")
async def get_intelligence(
    session_id: str,
    api_key: str = Security(verify_api_key)
):
    """Get extracted intelligence from a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "sessionId": session_id,
        "scamDetected": session.get("scam_detected", False),
        "confidenceScore": session.get("confidence_score", 0),
        "messagesExchanged": len(session.get("messages", [])),
        "extractedIntelligence": session.get("intelligence", {}),
        "agentNotes": session.get("agent_notes", []),
        "createdAt": session.get("created_at")
    }


@app.get("/api/all-sessions")
async def get_all_sessions(
    api_key: str = Security(verify_api_key)
):
    """Get list of all active sessions with their intelligence"""
    sessions_list = []
    for session_id, session_data in sessions.items():
        sessions_list.append({
            "sessionId": session_id,
            "scamDetected": session_data.get("scam_detected", False),
            "messagesExchanged": len(session_data.get("messages", [])),
            "upiExtracted": len(session_data.get("intelligence", {}).get("upiIds", [])),
            "phonesExtracted": len(session_data.get("intelligence", {}).get("phoneNumbers", [])),
            "linksExtracted": len(session_data.get("intelligence", {}).get("phishingLinks", [])),
            "createdAt": session_data.get("created_at")
        })
    return {"totalSessions": len(sessions_list), "sessions": sessions_list}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Interactive HTML dashboard to view all extracted intelligence"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🕵️ Agentic Honey-Pot Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                color: white;
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .stat-card h3 {
                color: #667eea;
                font-size: 1.2em;
                margin-bottom: 10px;
            }
            
            .stat-card .number {
                font-size: 2.5em;
                font-weight: bold;
                color: #764ba2;
            }
            
            .sessions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .session-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                border-left: 5px solid #667eea;
            }
            
            .session-card.scam {
                border-left-color: #e74c3c;
            }
            
            .session-card h3 {
                color: #333;
                margin-bottom: 10px;
                word-break: break-all;
            }
            
            .session-info {
                font-size: 0.9em;
                color: #666;
                margin-bottom: 15px;
            }
            
            .session-info p {
                margin: 5px 0;
            }
            
            .badge {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 5px;
                margin-bottom: 5px;
            }
            
            .badge.scam {
                background: #e74c3c;
                color: white;
            }
            
            .badge.safe {
                background: #2ecc71;
                color: white;
            }
            
            .intelligence-list {
                background: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .intelligence-item {
                font-family: 'Courier New', monospace;
                padding: 5px;
                background: white;
                margin: 5px 0;
                border-radius: 3px;
                font-size: 0.85em;
                word-break: break-all;
                border-left: 3px solid #667eea;
                padding-left: 8px;
            }
            
            .intelligence-item.upi { border-left-color: #3498db; }
            .intelligence-item.phone { border-left-color: #e67e22; }
            .intelligence-item.link { border-left-color: #e74c3c; }
            .intelligence-item.account { border-left-color: #9b59b6; }
            
            .refresh-btn {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                margin-bottom: 20px;
            }
            
            .refresh-btn:hover {
                background: #764ba2;
            }
            
            .no-data {
                text-align: center;
                color: white;
                padding: 40px;
                font-size: 1.2em;
            }
            
            .api-key-warning {
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕵️ Agentic Honey-Pot Intelligence Dashboard</h1>
                <p>Real-time scam detection and intelligence extraction</p>
            </div>
            
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <h3>Total Sessions</h3>
                    <div class="number" id="total-sessions">0</div>
                </div>
                <div class="stat-card">
                    <h3>Scams Detected</h3>
                    <div class="number" id="scams-detected">0</div>
                </div>
                <div class="stat-card">
                    <h3>UPI IDs Extracted</h3>
                    <div class="number" id="upis-extracted">0</div>
                </div>
                <div class="stat-card">
                    <h3>Phone Numbers</h3>
                    <div class="number" id="phones-extracted">0</div>
                </div>
            </div>
            
            <div id="sessions-container"></div>
        </div>
        
        <script>
            const API_KEY = "REPLACE_API_KEY";
            
            async function loadData() {
                try {
                    const response = await fetch('/api/all-sessions', {
                        headers: {
                            'x-api-key': API_KEY
                        }
                    });
                    
                    if (response.status === 403) {
                        alert('❌ Invalid API Key! Check your API_KEY environment variable.');
                        return;
                    }
                    
                    const data = await response.json();
                    displayData(data);
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('sessions-container').innerHTML = 
                        '<div class="no-data">❌ Failed to load data. Is the server running?</div>';
                }
            }
            
            async function displayData(data) {
                let totalUPIs = 0;
                let totalPhones = 0;
                let totalLinks = 0;
                let scamsCount = 0;
                
                let html = '';
                
                if (data.sessions.length === 0) {
                    html = '<div class="no-data">No sessions yet. Run test_scenarios.py to populate data.</div>';
                } else {
                    for (const session of data.sessions) {
                        const intelligence = await getSessionIntelligence(session.sessionId);
                        totalUPIs += (intelligence.extractedIntelligence?.upiIds?.length || 0);
                        totalPhones += (intelligence.extractedIntelligence?.phoneNumbers?.length || 0);
                        totalLinks += (intelligence.extractedIntelligence?.phishingLinks?.length || 0);
                        if (session.scamDetected) scamsCount++;
                        
                        html += renderSessionCard(session, intelligence);
                    }
                }
                
                document.getElementById('total-sessions').textContent = data.totalSessions;
                document.getElementById('scams-detected').textContent = scamsCount;
                document.getElementById('upis-extracted').textContent = totalUPIs;
                document.getElementById('phones-extracted').textContent = totalPhones;
                document.getElementById('sessions-container').innerHTML = html;
            }
            
            async function getSessionIntelligence(sessionId) {
                try {
                    const response = await fetch(`/api/intelligence/${sessionId}`, {
                        headers: {
                            'x-api-key': API_KEY
                        }
                    });
                    return await response.json();
                } catch {
                    return { upiIds: [], phoneNumbers: [], phishingLinks: [] };
                }
            }
            
            function renderSessionCard(session, intelligence) {
                const cardClass = session.scamDetected ? 'scam' : '';
                const badgeClass = session.scamDetected ? 'scam' : 'safe';
                const badgeText = session.scamDetected ? '🚨 SCAM' : '✅ SAFE';
                
                let intelligenceHtml = '';
                
                // UPI IDs
                for (const upi of intelligence.extractedIntelligence.upiIds || []) {
                    intelligenceHtml += `<div class="intelligence-item upi">💳 UPI: ${upi}</div>`;
                }
                
                // Phone Numbers
                for (const phone of intelligence.extractedIntelligence.phoneNumbers || []) {
                    intelligenceHtml += `<div class="intelligence-item phone">📱 Phone: ${phone}</div>`;
                }
                
                // Links
                for (const link of intelligence.extractedIntelligence.phishingLinks || []) {
                    intelligenceHtml += `<div class="intelligence-item link">🔗 Link: ${link}</div>`;
                }
                
                // Bank Accounts
                for (const account of intelligence.extractedIntelligence.bankAccounts || []) {
                    intelligenceHtml += `<div class="intelligence-item account">🏦 Account: ${account}</div>`;
                }
                
                if (!intelligenceHtml) {
                    intelligenceHtml = '<div style="padding: 10px; color: #999;">No intelligence extracted</div>';
                }
                
                const createdTime = new Date(intelligence.createdAt).toLocaleString();
                
                return `
                    <div class="session-card ${cardClass}">
                        <h3>Session: ${session.sessionId.substring(0, 50)}...</h3>
                        <div class="session-info">
                            <span class="badge ${badgeClass}">${badgeText}</span>
                            <p>📊 Messages Exchanged: <strong>${session.messagesExchanged}</strong></p>
                            <p>🕐 Created: ${createdTime}</p>
                        </div>
                        <div style="border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px;">
                            <strong style="color: #667eea;">📋 Extracted Intelligence:</strong>
                            <div class="intelligence-list">${intelligenceHtml}</div>
                        </div>
                    </div>
                `;
            }
            
            // Load data on page load and auto-refresh every 3 seconds
            loadData();
            setInterval(loadData, 3000);
        </script>
    </body>
    </html>
    """.replace("REPLACE_API_KEY", API_KEY)
    return html_content


@app.delete("/api/session/{session_id}")
async def delete_session(
    session_id: str,
    api_key: str = Security(verify_api_key)
):
    """Delete a session (cleanup)"""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "success", "message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
