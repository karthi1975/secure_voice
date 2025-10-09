#!/usr/bin/env python3
"""
VAPI Authentication Webhook Service
Deployable to Railway.app

Session-based authentication with sid parameter.
"""

from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
import time
import httpx

app = FastAPI(title="VAPI Auth Webhook", version="2.0.0")

# Enable CORS for VAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Valid credentials
VALID_CUSTOMER_ID = "urbanjungle"
VALID_PASSWORD = "alpha-bravo-123"

# Home Assistant configuration
HOMEASSISTANT_URL = os.getenv("HOMEASSISTANT_URL", "https://ut-demo-urbanjungle.homeadapt.us")
HOMEASSISTANT_WEBHOOK_ID = os.getenv("HOMEASSISTANT_WEBHOOK_ID", "vapi_air_circulator")

# In-memory session store (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = {}


class VapiMessage(BaseModel):
    """VAPI message structure"""
    type: str
    role: Optional[str] = None
    content: Optional[str] = None
    toolCalls: Optional[list] = None


class VapiCall(BaseModel):
    """VAPI call information"""
    id: Optional[str] = None
    assistantId: Optional[str] = None


class VapiWebhookRequest(BaseModel):
    """VAPI webhook request payload"""
    message: VapiMessage
    call: Optional[VapiCall] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "VAPI Authentication Webhook",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy"}


@app.post("/sessions")
async def create_session(request: Request):
    """
    Create a new session with credentials.

    Request body:
    {
      "customer_id": "urbanjungle",
      "password": "alpha-bravo-123"
    }

    Returns:
    {
      "sid": "uuid-string",
      "authenticated": false
    }
    """
    body = await request.json()
    customer_id = body.get("customer_id", "")
    password = body.get("password", "")

    # Create session ID
    sid = str(uuid.uuid4())

    # Store session
    sessions[sid] = {
        "customer_id": customer_id,
        "password": password,
        "authenticated": False,
        "created_at": time.time()
    }

    return {
        "sid": sid,
        "authenticated": False
    }


@app.post("/auth")
async def authenticate(request: Request, sid: str = Query(None)):
    """
    Authenticate VAPI voice session using sid parameter.

    Handles both:
    1. Tool function calls (home_auth)
    2. Generic server messages

    Returns:
    - Success: result with welcome message
    - Failure: result with "Authentication failed"
    """

    body = await request.json()
    message = body.get("message", {})
    message_type = message.get("type", "")

    # Get session from sid
    if not sid:
        return {
            "result": '{"success": false, "message": "No session ID provided"}'
        }

    session = sessions.get(sid)
    if not session:
        return {
            "result": '{"success": false, "message": "Invalid session ID"}'
        }

    # Validate credentials from session
    customer_id = session.get("customer_id", "")
    password = session.get("password", "")

    if customer_id == VALID_CUSTOMER_ID and password == VALID_PASSWORD:
        # Mark session as authenticated
        session["authenticated"] = True
        sessions[sid] = session

        success_message = "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"

        # Handle different message types
        if message_type == "function-call":
            # Response for function call
            return {
                "results": [{
                    "type": "function-result",
                    "name": "home_auth",
                    "result": success_message
                }]
            }
        elif message_type == "conversation-started":
            # Response for conversation started
            return {
                "firstMessage": success_message
            }
        else:
            # Generic response
            return {
                "result": f'{{"success": true, "message": "{success_message}"}}'
            }
    else:
        # Authentication failed
        if message_type == "function-call":
            return {
                "results": [{
                    "type": "function-result",
                    "name": "home_auth",
                    "result": "Authentication failed"
                }]
            }
        elif message_type == "conversation-started":
            return {
                "firstMessage": "Authentication failed"
            }
        else:
            return {
                "result": '{"success": false, "message": "Authentication failed"}'
            }


@app.post("/control")
async def control_device(request: Request, sid: str = Query(None)):
    """
    Control air circulator device.

    Called by control_air_circulator tool
    Checks if session is authenticated before allowing control.

    Returns:
    - Success: result with confirmation
    - Failure: result with error message
    """

    body = await request.json()
    message = body.get("message", {})
    message_type = message.get("type", "")

    # Get session from sid
    if not sid:
        return {
            "results": [{
                "type": "function-result",
                "name": "control_air_circulator",
                "result": "No session ID provided"
            }]
        }

    session = sessions.get(sid)
    if not session:
        return {
            "results": [{
                "type": "function-result",
                "name": "control_air_circulator",
                "result": "Invalid session ID"
            }]
        }

    # Check if authenticated
    if not session.get("authenticated", False):
        return {
            "results": [{
                "type": "function-result",
                "name": "control_air_circulator",
                "result": "Not authenticated. Please authenticate first."
            }]
        }

    # Extract function call parameters
    function_call = message.get("functionCall", {})
    parameters = function_call.get("parameters", {})

    device = parameters.get("device", "")
    action = parameters.get("action", "")

    if not device or not action:
        return {
            "results": [{
                "type": "function-result",
                "name": "control_air_circulator",
                "result": "Missing device or action"
            }]
        }

    # Forward to Home Assistant webhook
    try:
        async with httpx.AsyncClient() as client:
            ha_webhook_url = f"{HOMEASSISTANT_URL}/api/webhook/{HOMEASSISTANT_WEBHOOK_ID}"

            # Transform to Home Assistant expected format
            # Home Assistant webhook receives data at root level (not nested in "message")
            ha_payload = {
                "toolCalls": [{
                    "function": {
                        "arguments": {
                            "device": device,
                            "action": action
                        }
                    }
                }]
            }

            # Send to Home Assistant
            ha_response = await client.post(
                ha_webhook_url,
                json=ha_payload,
                timeout=10.0
            )

            if ha_response.status_code == 200:
                result_message = f"{device.capitalize()} {action.replace('_', ' ')}"
            else:
                result_message = f"Error: Home Assistant returned {ha_response.status_code}"

    except Exception as e:
        result_message = f"Error calling Home Assistant: {str(e)}"

    return {
        "results": [{
            "type": "function-result",
            "name": "control_air_circulator",
            "result": result_message
        }]
    }


@app.post("/webhook")
async def webhook_unified(request: Request, sid: str = Query(None)):
    """
    Unified webhook endpoint that routes to auth or control based on function name.

    This endpoint handles all VAPI server messages when using serverUrl with ?sid=xxx
    """
    body = await request.json()
    message = body.get("message", {})
    message_type = message.get("type", "")

    # Route based on function name
    if message_type == "function-call":
        function_call = message.get("functionCall", {})
        function_name = function_call.get("name", "")

        if function_name == "home_auth":
            # Route to auth handler
            return await authenticate(request, sid)
        elif function_name == "control_air_circulator":
            # Route to control handler
            return await control_device(request, sid)
        else:
            return {
                "results": [{
                    "type": "function-result",
                    "name": function_name,
                    "result": f"Unknown function: {function_name}"
                }]
            }
    elif message_type == "conversation-started":
        # Route to auth for conversation started
        return await authenticate(request, sid)
    else:
        return {
            "results": [{
                "type": "assistant-message",
                "message": f"Unhandled message type: {message_type}"
            }]
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
