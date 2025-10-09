# Simplified Authentication System

## Overview

The authentication system has been **simplified** to remove password requirements and use VAPI's Bearer token authentication instead.

## What Changed

### ❌ Old System (Complex)
```
Client → Create session with customer_id + password
Server → Validate password, store session
VAPI → Call webhook with ?sid=xxx
Server → Lookup session, check if authenticated
```

### ✅ New System (Simplified)
```
VAPI → Send Bearer token + x-customer-id header
Server → Validate Bearer token = proves VAPI request
Server → Map customer_id → HA instance
Server → Route commands to correct HA
```

---

## Authentication Flow

### 1. VAPI Sends Request

When VAPI calls your webhook, it includes:

**Headers:**
```
Authorization: Bearer e4077034-d96a-41c7-8f49-e36accb11fb4
x-customer-id: urbanjungle
```

### 2. Server Validates

The webhook validates:
- ✅ Bearer token matches `VAPI_API_KEY` → proves request is from VAPI
- ✅ `x-customer-id` is present → identifies which customer

### 3. Server Maps Customer → HA

```python
# webhook_service/ha_instances.py
HA_INSTANCES = {
    "urbanjungle": {
        "customer_id": "urbanjungle",
        "ha_url": "https://ut-demo-urbanjungle.homeadapt.us",
        "ha_webhook_id": "vapi_air_circulator",
        "name": "Urban Jungle Demo"
    }
}
```

### 4. Server Routes Commands

Commands are automatically routed to the correct HA instance based on `customer_id`.

---

## Files Updated

### webhook_service/main.py
- Added `validate_vapi_request()` function to validate Bearer token + customer_id
- Updated `/webhook` endpoint to extract headers and map to HA instance
- Simplified `home_auth` - no longer needs password validation
- Updated `control_air_circulator` - uses mapped HA instance

### webhook_service/ha_instances.py
- **Removed password field** from HA_INSTANCES
- **Removed validate_credentials()** function
- Simplified to just `get_ha_instance(customer_id)`

### config/config.json
- **Removed password field**
- Only needs: customer_id, vapi_api_key, vapi_assistant_id, server_url

### src/vapi_client_clean.py
- **Removed password handling**
- Updated session creation to only send customer_id
- Simplified display messages

---

## Environment Variables Required

Add to Railway:

```bash
VAPI_API_KEY=e4077034-d96a-41c7-8f49-e36accb11fb4
```

This is used to validate the Bearer token from VAPI.

---

## How to Configure VAPI

### Option 1: Via VAPI Dashboard (Credentials)

1. Go to https://dashboard.vapi.ai/credentials
2. Create new Bearer Token credential:
   - **Name**: `SecureVoice Auth`
   - **Token**: `e4077034-d96a-41c7-8f49-e36accb11fb4`
3. Get the credential ID (e.g., `cred_abc123`)
4. Configure assistant to use this credential for serverUrl

### Option 2: Via Server URL Configuration

In VAPI assistant settings:
```json
{
  "serverUrl": "https://securevoice-production-f5c9.up.railway.app/webhook",
  "serverUrlSecret": {
    "provider": "Bearer",
    "token": "e4077034-d96a-41c7-8f49-e36accb11fb4"
  }
}
```

### Custom Header for customer_id

VAPI needs to send `x-customer-id` header. This can be configured via:
- Assistant metadata
- Server URL parameters
- Custom headers in VAPI configuration

---

## Testing

### 1. Test Session Creation (No Password)

```bash
curl -X POST "https://securevoice-production-f5c9.up.railway.app/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "urbanjungle"
  }'
```

Expected response:
```json
{
  "sid": "uuid-here",
  "customer_id": "urbanjungle",
  "authenticated": false
}
```

### 2. Test Webhook with Bearer Token

```bash
curl -X POST "https://securevoice-production-f5c9.up.railway.app/webhook" \
  -H "Authorization: Bearer e4077034-d96a-41c7-8f49-e36accb11fb4" \
  -H "x-customer-id: urbanjungle" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "function": {
          "name": "home_auth",
          "arguments": {}
        }
      }]
    }
  }'
```

Expected response:
```json
{
  "results": [{
    "type": "function-result",
    "name": "home_auth",
    "result": "Welcome! Authentication successful. I'm Luna, controlling Urban Jungle Demo. How can I help you today?"
  }]
}
```

### 3. Test with Python Client

```bash
./venv/bin/python src/vapi_client_clean.py
```

---

## Benefits of Simplified Authentication

1. ✅ **No passwords to manage** - simpler for customers
2. ✅ **More secure** - Bearer token validates VAPI requests
3. ✅ **Easier to scale** - just add new customer_id entries
4. ✅ **Cleaner code** - removed password validation logic
5. ✅ **Faster authentication** - no password checks needed

---

## Adding New Customers

To add a new customer, just add to `webhook_service/ha_instances.py`:

```python
HA_INSTANCES = {
    "urbanjungle": { ... },
    "customer2": {
        "customer_id": "customer2",
        "ha_url": "https://customer2.homeadapt.us",
        "ha_webhook_id": "vapi_air_circulator",
        "name": "Customer 2 Home"
    }
}
```

No passwords needed!

---

## Security Notes

- **Bearer token** must be kept secret - acts as API key
- Only VAPI should know this token
- Token validates that requests are from VAPI, not unauthorized sources
- customer_id in header identifies which customer, but Bearer token proves authenticity

---

**Version**: 3.0.0
**Date**: 2025-10-09
**Status**: Ready for deployment
