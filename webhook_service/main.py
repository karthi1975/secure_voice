#!/usr/bin/env python3
"""
VAPI Authentication Webhook Service
Deployable to Railway.app

Simplified Authentication System:
- Bearer token validates VAPI requests
- customer_id in headers identifies which HA instance
- No password required - simpler flow
- Routes commands to correct HA based on customer_id

Updated: 2025-10-09 - Simplified authentication with Bearer token + customer_id
"""

from fastapi import FastAPI, Request, Query, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
import time
import httpx

# Import HA instances configuration
from ha_instances import get_ha_instance

app = FastAPI(title="VAPI Auth Webhook", version="3.0.0")  # Simplified Auth

# Enable CORS for VAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VAPI API Key for Bearer token validation
VAPI_API_KEY = os.getenv("VAPI_API_KEY", "e4077034-d96a-41c7-8f49-e36accb11fb4")

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


def validate_vapi_request(authorization: Optional[str] = Header(None),
                          x_customer_id: Optional[str] = Header(None, alias="x-customer-id")):
    """
    Middleware to validate VAPI requests.

    Validates:
    1. Bearer token matches VAPI_API_KEY
    2. x-customer-id header is present

    Returns: customer_id if valid
    Raises: HTTPException if invalid
    """
    # Validate Bearer token
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix
    if token != VAPI_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Validate customer_id header
    if not x_customer_id:
        raise HTTPException(status_code=401, detail="Missing x-customer-id header")

    return x_customer_id


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "VAPI Authentication Webhook",
        "status": "healthy",
        "version": "3.0.0",
        "auth": "Bearer token + customer_id"
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy"}


@app.post("/sessions")
async def create_session(request: Request):
    """
    Create a new session with customer_id only (no password needed).

    Request body:
    {
      "customer_id": "urbanjungle"
    }

    Returns:
    {
      "sid": "uuid-string",
      "customer_id": "urbanjungle",
      "authenticated": false
    }
    """
    body = await request.json()
    customer_id = body.get("customer_id", "")

    # Validate customer exists
    ha_instance = get_ha_instance(customer_id)
    if not ha_instance:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    # Create session ID
    sid = str(uuid.uuid4())

    # Store session
    sessions[sid] = {
        "customer_id": customer_id,
        "ha_instance": ha_instance,
        "authenticated": False,
        "created_at": time.time()
    }

    return {
        "sid": sid,
        "customer_id": customer_id,
        "authenticated": False
    }


@app.post("/auth")
async def authenticate(request: Request, sid: str = Query(None)):
    """
    Authenticate VAPI voice session using sid parameter.

    Simplified flow:
    - Session already has HA instance from /sessions creation
    - Just mark session as authenticated and return welcome message

    Returns:
    - Success: result with welcome message
    - Failure: result with error message
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

    # Check if session expired
    session_age = time.time() - session.get("created_at", 0)
    if session_age > SESSION_TIMEOUT:
        # Session expired, remove it
        del sessions[sid]
        return {
            "result": '{"success": false, "message": "Session expired. Please reconnect."}'
        }

    # Get HA instance from session (already stored during session creation)
    ha_instance = session.get("ha_instance")
    customer_id = session.get("customer_id", "")

    if ha_instance:
        # Mark session as authenticated
        session["authenticated"] = True
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
        # No HA instance found (shouldn't happen if session was created properly)
        error_msg = f"No HA instance found for customer: {customer_id}"
        if message_type in ["function-call", "tool-calls"]:
            return {
                "results": [{
                    "type": "function-result",
                    "name": "home_auth",
                    "result": error_msg
                }]
            }
        elif message_type == "conversation-started":
            return {
                "firstMessage": error_msg
            }
        else:
            return {
                "result": f'{{"success": false, "message": "{error_msg}"}}'
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
async def webhook_unified(
    request: Request,
    sid: str = Query(None),
    authorization: Optional[str] = Header(None),
    x_customer_id: Optional[str] = Header(None, alias="x-customer-id")
):
    """
    Unified webhook endpoint that handles all VAPI events.

    Simplified Authentication Flow:
    1. VAPI sends Bearer token + x-customer-id header
    2. Validate Bearer token matches VAPI_API_KEY
    3. Map customer_id → HA instance
    4. Handle tool calls (home_auth, control_air_circulator)

    Headers expected:
    - Authorization: Bearer {VAPI_API_KEY}
    - x-customer-id: {customer_id} (e.g., "urbanjungle")

    Query params:
    - sid: Session ID (optional, for session tracking)
    """
    body = await request.json()

    # DEBUG: Log the entire payload
    print(f"🔍 WEBHOOK - Headers: Authorization={authorization[:20]}..., x-customer-id={x_customer_id}")
    print(f"🔍 WEBHOOK - SID: {sid}")

    # Validate VAPI request (Bearer token + customer_id)
    if authorization and x_customer_id:
        try:
            customer_id = validate_vapi_request(authorization, x_customer_id)
            print(f"✅ VAPI request validated for customer: {customer_id}")

            # Map customer_id → HA instance
            ha_instance = get_ha_instance(customer_id)
            if not ha_instance:
                raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

            print(f"✅ Mapped to HA: {ha_instance.get('name')}")

        except HTTPException as e:
            print(f"❌ Authentication failed: {e.detail}")
            raise
    else:
        # No authentication headers - allow for backward compatibility
        customer_id = None
        ha_instance = None
        print(f"⚠️  No authentication headers - using default HA")

    message = body.get("message", {})
    message_type = message.get("type", "")

    print(f"🔍 WEBHOOK - Message type: {message_type}")

    # Handle status-update events (call lifecycle tracking)
    if message_type == "status-update":
        status = message.get("status", "")
        call = body.get("call", {})
        call_id = call.get("id", "unknown")
        print(f"📞 Call {call_id} status: {status}")

        # Track session activity if sid provided
        if sid and sid in sessions:
            sessions[sid]["last_activity"] = time.time()
            sessions[sid]["call_status"] = status

        return {"message": "Status update received"}

    # Handle transcript events (speech-to-text logging)
    if message_type == "transcript":
        transcript_text = message.get("transcript", "")
        transcript_type = message.get("transcriptType", "partial")
        role = message.get("role", "unknown")
        print(f"💬 Transcript ({transcript_type}) [{role}]: {transcript_text}")

        return {"message": "Transcript received"}

    # Handle assistant-request events (dynamic assistant configuration)
    if message_type == "assistant-request":
        print(f"🤖 Assistant request received")

        # If we have a session, we can return a customized assistant
        if sid and sid in sessions:
            session = sessions[sid]
            customer_id = session.get("customer_id", "unknown")
            print(f"🤖 Returning assistant for customer: {customer_id}")

        # Return the pre-configured assistant ID
        # (In future, could return transient assistant with custom config)
        return {
            "assistant": {
                "assistantId": os.getenv("VAPI_ASSISTANT_ID", "31377f1e-dd62-43df-bc3c-ca8e87e08138")
            }
        }

    # Handle end-of-call-report events (call summary)
    if message_type == "end-of-call-report":
        call = body.get("call", {})
        call_id = call.get("id", "unknown")
        duration = message.get("endedReason", "unknown")
        print(f"📊 Call {call_id} ended: {duration}")

        # Clean up session tracking
        if sid and sid in sessions:
            sessions[sid]["last_call_ended"] = time.time()

        return {"message": "Call report received"}

    # Handle conversation-update events (track conversation history)
    if message_type == "conversation-update":
        conversation = message.get("conversation", [])
        print(f"💭 Conversation updated: {len(conversation)} messages")

        # Track conversation in session
        if sid and sid in sessions:
            sessions[sid]["conversation_length"] = len(conversation)

        return {"message": "Conversation update received"}

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

            # Use mapped HA instance if available, otherwise use default
            if ha_instance:
                target_ha_url = ha_instance.get("ha_url", HOMEASSISTANT_URL)
                target_webhook_id = ha_instance.get("ha_webhook_id", HOMEASSISTANT_WEBHOOK_ID)
                print(f"🏠 Using HA for {customer_id}: {target_ha_url}")
            else:
                target_ha_url = HOMEASSISTANT_URL
                target_webhook_id = HOMEASSISTANT_WEBHOOK_ID
                print(f"🏠 Using default HA: {target_ha_url}")

            # Forward to Home Assistant webhook
            try:
                async with httpx.AsyncClient() as client:
                    ha_webhook_url = f"{target_ha_url}/api/webhook/{target_webhook_id}"

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
        elif function_name == "home_auth":
            # Simplified auth: customer_id already validated, just return welcome message
            if ha_instance and customer_id:
                ha_name = ha_instance.get("name", "your home")
                success_message = f"Welcome! Authentication successful. I'm Luna, controlling {ha_name}. How can I help you today?"

                return {
                    "results": [{
                        "type": "function-result",
                        "name": "home_auth",
                        "result": success_message
                    }]
                }
            elif sid:
                # Fallback to session-based auth (backward compatibility)
                return await authenticate(request, sid)
            else:
                return {
                    "results": [{
                        "type": "function-result",
                        "name": "home_auth",
                        "result": "Authentication failed: No customer_id or session ID"
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
