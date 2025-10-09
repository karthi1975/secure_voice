#!/usr/bin/env python3
"""
VAPI Secure Proxy Service
Deployable to Railway.app

Tier 0 Security Architecture:
- Edge devices (Pi) never hold VAPI API key
- Device authenticates with device_secret → gets short-lived JWT (15 min TTL)
- Pi calls proxy endpoints with JWT token
- Proxy holds VAPI_API_KEY and forwards requests
- Supports token refresh for ongoing sessions

Updated: 2025-10-09 - Secure proxy with JWT tokens
"""

from fastapi import FastAPI, Request, Query, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import uuid
import time
import httpx

# Import modules
from ha_instances import get_ha_instance
from device_auth import (
    validate_device_credentials,
    generate_device_token,
    verify_device_token,
    get_device_info,
    get_customer_id_from_device,
    TOKEN_TTL_MINUTES
)

app = FastAPI(title="VAPI Secure Proxy", version="4.0.0")  # Secure Proxy with JWT

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


def verify_device_jwt(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Dependency to verify device JWT token.

    Returns:
        Token payload if valid
    Raises:
        HTTPException if invalid/expired
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix
    payload = verify_device_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "VAPI Secure Proxy",
        "status": "healthy",
        "version": "4.0.0",
        "auth": "Device JWT tokens (15 min TTL)",
        "endpoints": {
            "device_auth": "/device/auth",
            "token_refresh": "/device/refresh",
            "vapi_proxy": "/vapi/*"
        }
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy"}


# ========================================
# Device Authentication Endpoints
# ========================================

@app.post("/device/auth")
async def device_authenticate(request: Request):
    """
    Authenticate device and issue short-lived JWT token.

    Request body:
    {
      "device_id": "pi_urbanjungle_001",
      "device_secret": "dev_secret_urbanjungle_abc123xyz"
    }

    Returns:
    {
      "access_token": "jwt-token-here",
      "token_type": "Bearer",
      "expires_in": 900,
      "customer_id": "urbanjungle",
      "device_info": {...}
    }
    """
    body = await request.json()
    device_id = body.get("device_id", "")
    device_secret = body.get("device_secret", "")

    if not device_id or not device_secret:
        raise HTTPException(status_code=400, detail="device_id and device_secret required")

    # Validate device credentials
    device = validate_device_credentials(device_id, device_secret)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device credentials")

    # Generate JWT token
    customer_id = device["customer_id"]
    token = generate_device_token(device_id, customer_id)

    # Get device info (without secret)
    device_info = get_device_info(device_id)

    print(f"✅ Device authenticated: {device_id} → customer: {customer_id}")

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": TOKEN_TTL_MINUTES * 60,  # seconds
        "customer_id": customer_id,
        "device_info": device_info
    }


@app.post("/device/refresh")
async def device_refresh_token(token_payload: Dict[str, Any] = Depends(verify_device_jwt)):
    """
    Refresh device JWT token (must have valid token to refresh).

    Headers:
        Authorization: Bearer {current-jwt-token}

    Returns:
    {
      "access_token": "new-jwt-token-here",
      "token_type": "Bearer",
      "expires_in": 900
    }
    """
    device_id = token_payload["device_id"]
    customer_id = token_payload["customer_id"]

    # Generate new token
    new_token = generate_device_token(device_id, customer_id)

    print(f"🔄 Token refreshed for device: {device_id}")

    return {
        "access_token": new_token,
        "token_type": "Bearer",
        "expires_in": TOKEN_TTL_MINUTES * 60
    }


@app.get("/device/info")
async def device_get_info(token_payload: Dict[str, Any] = Depends(verify_device_jwt)):
    """
    Get device information.

    Headers:
        Authorization: Bearer {jwt-token}

    Returns device info for authenticated device.
    """
    device_id = token_payload["device_id"]
    device_info = get_device_info(device_id)

    if not device_info:
        raise HTTPException(status_code=404, detail="Device not found")

    return device_info


# ========================================
# VAPI Proxy Endpoints
# ========================================

@app.post("/vapi/start")
async def vapi_proxy_start(
    request: Request,
    token_payload: Dict[str, Any] = Depends(verify_device_jwt)
):
    """
    Proxy VAPI call start request.

    Pi sends JWT token → Proxy validates → Proxy calls VAPI with real API key.

    Request body (from Pi):
    {
      "assistant_id": "...",
      "assistant_overrides": {...}
    }

    Returns VAPI response.
    """
    device_id = token_payload["device_id"]
    customer_id = token_payload["customer_id"]

    print(f"📞 VAPI start call from device: {device_id} (customer: {customer_id})")

    body = await request.json()
    assistant_id = body.get("assistant_id")
    assistant_overrides = body.get("assistant_overrides", {})

    if not assistant_id:
        raise HTTPException(status_code=400, detail="assistant_id required")

    # Get VAPI API key from environment (never exposed to Pi)
    vapi_api_key = os.getenv("VAPI_API_KEY")
    if not vapi_api_key:
        raise HTTPException(status_code=500, detail="VAPI_API_KEY not configured on server")

    # Call VAPI API on behalf of device (use /call/web for web calls)
    # Format matches vapi-python SDK: {'assistantId': ..., 'assistantOverrides': ...}
    try:
        async with httpx.AsyncClient() as client:
            vapi_response = await client.post(
                "https://api.vapi.ai/call/web",
                headers={
                    "Authorization": f"Bearer {vapi_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "assistantId": assistant_id,
                    "assistantOverrides": assistant_overrides
                },
                timeout=30.0
            )

            vapi_response.raise_for_status()
            result = vapi_response.json()

            print(f"✅ VAPI call started: {result.get('id', 'unknown')}")

            return result

    except httpx.HTTPStatusError as e:
        print(f"❌ VAPI API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"VAPI API error: {e.response.text}"
        )
    except Exception as e:
        print(f"❌ Error calling VAPI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling VAPI: {str(e)}")


@app.post("/vapi/stop")
async def vapi_proxy_stop(
    request: Request,
    token_payload: Dict[str, Any] = Depends(verify_device_jwt)
):
    """
    Proxy VAPI call stop request.

    Request body:
    {
      "call_id": "..."
    }
    """
    device_id = token_payload["device_id"]
    body = await request.json()
    call_id = body.get("call_id")

    if not call_id:
        raise HTTPException(status_code=400, detail="call_id required")

    print(f"🛑 VAPI stop call from device: {device_id}, call: {call_id}")

    # Get VAPI API key
    vapi_api_key = os.getenv("VAPI_API_KEY")
    if not vapi_api_key:
        raise HTTPException(status_code=500, detail="VAPI_API_KEY not configured")

    # Stop VAPI call (use PATCH method, not POST)
    try:
        async with httpx.AsyncClient() as client:
            vapi_response = await client.patch(
                f"https://api.vapi.ai/call/{call_id}",
                headers={
                    "Authorization": f"Bearer {vapi_api_key}",
                    "Content-Type": "application/json"
                },
                json={"status": "ended"},
                timeout=30.0
            )

            vapi_response.raise_for_status()
            result = vapi_response.json()

            print(f"✅ VAPI call stopped: {call_id}")

            return result

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"VAPI API error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping VAPI call: {str(e)}")


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
            # HA automation expects: trigger.json.message.toolCalls
            ha_payload = {
                "message": {
                    "toolCalls": [{
                        "function": {
                            "arguments": {
                                "device": device,
                                "action": action
                            }
                        }
                    }]
                }
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
    device_id: str = Query(None),
    authorization: Optional[str] = Header(None),
    x_customer_id: Optional[str] = Header(None, alias="x-customer-id")
):
    """
    Unified webhook endpoint that handles all VAPI events.

    Multi-Tenant Routing Options:
    1. device_id query param (NEW - from secure proxy client)
    2. x-customer-id header (VAPI native)
    3. sid query param (legacy session-based)

    Priority: device_id > x-customer-id > sid

    Query params:
    - device_id: Device identifier (e.g., "pi_urbanjungle_001") - maps to customer
    - sid: Session ID (optional, legacy)

    Headers:
    - Authorization: Bearer {VAPI_API_KEY}
    - x-customer-id: {customer_id} (optional, e.g., "urbanjungle")
    """
    body = await request.json()

    # DEBUG: Log the entire payload
    print(f"🔍 WEBHOOK - device_id={device_id}, sid={sid}, x-customer-id={x_customer_id}")

    # Multi-tenant routing: device_id → customer_id → HA instance
    customer_id = None
    ha_instance = None

    # Option 1: device_id query param (secure proxy client)
    if device_id:
        customer_id = get_customer_id_from_device(device_id)
        if not customer_id:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        ha_instance = get_ha_instance(customer_id)
        if not ha_instance:
            raise HTTPException(status_code=404, detail=f"HA instance for customer {customer_id} not found")

        print(f"✅ Routed via device_id: {device_id} → customer: {customer_id} → HA: {ha_instance.get('name')}")

    # Option 2: x-customer-id header (VAPI native)
    elif authorization and x_customer_id:
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

    # Option 3: sid query param (legacy session-based)
    elif sid:
        # Use session-based routing (backward compatibility)
        customer_id = None
        ha_instance = None
        print(f"⚠️  Using legacy sid-based routing: {sid}")

    else:
        # No routing info - allow for backward compatibility
        customer_id = None
        ha_instance = None
        print(f"⚠️  No routing info - using default HA")

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

        if function_name == "control_front_door":
            # Handle front door control
            parameters = function_call.get("parameters", {}) or function_call.get("arguments", {})

            # If arguments is a string, parse it as JSON
            if isinstance(parameters, str):
                import json
                parameters = json.loads(parameters)

            action = parameters.get("action", "")

            if not action:
                return {
                    "results": [{
                        "type": "function-result",
                        "name": "control_front_door",
                        "result": "Missing action"
                    }]
                }

            # Use mapped HA instance if available
            if ha_instance:
                target_ha_url = ha_instance.get("ha_url", HOMEASSISTANT_URL)
                target_webhook_id = ha_instance.get("ha_webhook_id", HOMEASSISTANT_WEBHOOK_ID)
                print(f"🚪 Front door command for {customer_id}: {action}")
            else:
                target_ha_url = HOMEASSISTANT_URL
                target_webhook_id = HOMEASSISTANT_WEBHOOK_ID
                print(f"🚪 Front door command: {action}")

            # Forward to Home Assistant webhook
            try:
                async with httpx.AsyncClient() as client:
                    ha_webhook_url = f"{target_ha_url}/api/webhook/{target_webhook_id}"

                    # Transform to Home Assistant expected format
                    # HA automation expects: trigger.json.message.toolCalls
                    ha_payload = {
                        "message": {
                            "toolCalls": [{
                                "function": {
                                    "arguments": {
                                        "device": "front_door",
                                        "action": action
                                    }
                                }
                            }]
                        }
                    }

                    # Send to Home Assistant
                    ha_response = await client.post(
                        ha_webhook_url,
                        json=ha_payload,
                        timeout=10.0
                    )

                    if ha_response.status_code == 200:
                        result_message = f"Front door {action}"
                    else:
                        result_message = f"Error: Home Assistant returned {ha_response.status_code}"

            except Exception as e:
                result_message = f"Error calling Home Assistant: {str(e)}"

            return {
                "results": [{
                    "type": "function-result",
                    "name": "control_front_door",
                    "result": result_message
                }]
            }
        elif function_name == "control_air_circulator":
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
                    # HA automation expects: trigger.json.message.toolCalls
                    ha_payload = {
                        "message": {
                            "toolCalls": [{
                                "function": {
                                    "arguments": {
                                        "device": device,
                                        "action": action
                                    }
                                }
                            }]
                        }
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
