#!/usr/bin/env python3
"""
VAPI Authentication Webhook Service
Deployable to Railway.app

Session-based authentication with sid parameter.

IMPORTANT: VAPI tools should NOT have server URLs configured.
Client's assistant_overrides.serverUrl (with ?sid=xxx) must take precedence.
Updated: 2025-10-09 - Cleared tool-level server URLs for proper SID routing
"""

from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
import time
import httpx

# Import HA instances configuration
from ha_instances import validate_credentials, get_ha_instance

app = FastAPI(title="VAPI Auth Webhook", version="2.1.0")  # Multi-HA support

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

# Session timeout (7 days in seconds) - increased for reliable authentication
SESSION_TIMEOUT = 7 * 24 * 60 * 60

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

    # Check if session expired (24 hours)
    session_age = time.time() - session.get("created_at", 0)
    if session_age > SESSION_TIMEOUT:
        # Session expired, remove it
        del sessions[sid]
        return {
            "result": '{"success": false, "message": "Session expired. Please reconnect."}'
        }

    # Validate credentials from session
    customer_id = session.get("customer_id", "")
    password = session.get("password", "")

    # Validate against HA instances configuration
    ha_instance = validate_credentials(customer_id, password)

    if ha_instance:
        # Mark session as authenticated and store HA instance info
        session["authenticated"] = True
        session["ha_instance"] = ha_instance
        sessions[sid] = session

        ha_name = ha_instance.get("name", "your home")
        success_message = f"Welcome! Authentication successful. I'm Luna, controlling {ha_name}. How can I help you today?"

        # Handle different message types
        if message_type in ["function-call", "tool-calls"]:
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
        if message_type in ["function-call", "tool-calls"]:
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

    # Check if session expired
    session_age = time.time() - session.get("created_at", 0)
    if session_age > SESSION_TIMEOUT:
        del sessions[sid]
        return {
            "results": [{
                "type": "function-result",
                "name": "control_air_circulator",
                "result": "Session expired. Please reconnect."
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

    # Extract function call parameters (handle both formats)
    function_call = message.get("functionCall", {})

    # If toolCalls array exists, use the first one
    if not function_call and message.get("toolCalls"):
        tool_calls = message.get("toolCalls", [])
        if tool_calls:
            first_tool_call = tool_calls[0]
            function_call = first_tool_call.get("function", {})

    # Handle both "parameters" and "arguments" fields
    parameters = function_call.get("parameters", {}) or function_call.get("arguments", {})

    # If arguments is a string, parse it as JSON
    if isinstance(parameters, str):
        import json
        parameters = json.loads(parameters)

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

    # Get HA instance from session
    ha_instance = session.get("ha_instance", {})
    ha_url = ha_instance.get("ha_url", HOMEASSISTANT_URL)
    ha_webhook_id = ha_instance.get("ha_webhook_id", HOMEASSISTANT_WEBHOOK_ID)

    # Forward to Home Assistant webhook
    try:
        async with httpx.AsyncClient() as client:
            ha_webhook_url = f"{ha_url}/api/webhook/{ha_webhook_id}"

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

    Two modes:
    1. With sid parameter: Authenticated mode (requires home_auth first)
    2. Without sid parameter: Direct passthrough mode (forwards to Home Assistant)
    """
    body = await request.json()

    # DEBUG: Log the entire payload to see what VAPI sends
    print(f"🔍 WEBHOOK DEBUG - Full payload: {body}")
    print(f"🔍 WEBHOOK DEBUG - SID: {sid}")

    message = body.get("message", {})
    message_type = message.get("type", "")

    print(f"🔍 WEBHOOK DEBUG - Message type: {message_type}")

    # Handle both "function-call" and "tool-calls" message types
    if message_type in ["function-call", "tool-calls"]:
        # Handle both formats: functionCall (singular) and toolCalls (array)
        function_call = message.get("functionCall", {})

        # If toolCalls array exists, use the first one
        if not function_call and message.get("toolCalls"):
            tool_calls = message.get("toolCalls", [])
            if tool_calls:
                first_tool_call = tool_calls[0]
                function_call = first_tool_call.get("function", {})

        function_name = function_call.get("name", "")

        if function_name == "control_air_circulator":
            # If no sid, use unauthenticated mode
            if not sid:
                # Handle both "parameters" and "arguments" fields
                parameters = function_call.get("parameters", {}) or function_call.get("arguments", {})

                # If arguments is a string, parse it as JSON
                if isinstance(parameters, str):
                    import json
                    parameters = json.loads(parameters)

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
            else:
                # With sid, use authenticated mode
                return await control_device(request, sid)
        elif function_name == "home_auth":
            # Route to auth handler (only with sid)
            if sid:
                return await authenticate(request, sid)
            else:
                return {
                    "results": [{
                        "type": "function-result",
                        "name": "home_auth",
                        "result": "No session ID provided for authentication"
                    }]
                }
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
