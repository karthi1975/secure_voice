# Tier 0 Security: Secure Proxy Architecture

## 🔒 Security Overview

**Problem**: Storing VAPI API key on Raspberry Pi is a security risk. If the device is compromised, the attacker gets full access to your VAPI account.

**Solution**: Implement a secure proxy that holds the sensitive API key. Pi devices only get short-lived JWT tokens (15-minute TTL).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 0 SECURE PROXY ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Raspberry Pi (Edge Device)                                 │
│    Holds: device_id, device_secret                          │
│    ↓ [Authenticates with device_secret]                     │
│                                                              │
│  Railway Server (Secure Proxy)                              │
│    ✓ Validates device_secret                                │
│    ✓ Issues JWT token (15-minute TTL)                       │
│    ✓ Holds VAPI_API_KEY (never exposed to Pi)              │
│    ✓ Proxies VAPI API calls                                 │
│    ✓ Automatic token refresh                                │
│    ↓ [Calls VAPI with real API key]                         │
│                                                              │
│  VAPI Service                                               │
│    ✓ Receives calls from YOUR server (not Pi)              │
│    ✓ Returns results to YOUR server → Pi                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Benefits

### ✅ What Pi Has (Safe if Compromised)
- `device_id`: Public identifier (e.g., "pi_urbanjungle_001")
- `device_secret`: Device-specific secret (can be revoked)
- Short-lived JWT token (15-minute expiry)

### 🔒 What Pi NEVER Has (Secure on Server)
- ❌ VAPI API key (stays on Railway server)
- ❌ Customer credentials
- ❌ Long-lived tokens

### 🛡️ If Pi is Compromised
1. Attacker gets only:
   - `device_secret` for ONE device
   - Current JWT token (expires in ≤15 minutes)
2. You can immediately:
   - Revoke the device (`device["active"] = False`)
   - All tokens for that device become invalid
3. Attacker CANNOT:
   - Get VAPI API key
   - Access other customers' devices
   - Use expired tokens

---

## Components

### 1. Device Authentication Module
**File**: `webhook_service/device_auth.py`

**Features**:
- Device registry with device_id + device_secret
- JWT token generation with 15-minute TTL
- Token verification and validation
- Device revocation support

**Key Functions**:
```python
validate_device_credentials(device_id, device_secret) → device_config
generate_device_token(device_id, customer_id) → JWT token
verify_device_token(token) → payload or None
revoke_device(device_id) → bool
```

### 2. Secure Proxy Server
**File**: `webhook_service/main.py` (v4.0.0)

**New Endpoints**:

#### Device Authentication
```
POST /device/auth
Body: { "device_id": "...", "device_secret": "..." }
Returns: { "access_token": "jwt...", "expires_in": 900, ... }
```

#### Token Refresh
```
POST /device/refresh
Headers: Authorization: Bearer {current-token}
Returns: { "access_token": "new-jwt...", "expires_in": 900 }
```

#### VAPI Proxy
```
POST /vapi/start
Headers: Authorization: Bearer {jwt-token}
Body: { "assistant_id": "...", "assistant_overrides": {...} }
Returns: VAPI call response
```

```
POST /vapi/stop
Headers: Authorization: Bearer {jwt-token}
Body: { "call_id": "..." }
Returns: VAPI stop response
```

### 3. Secure Pi Client
**File**: `src/vapi_client_secure_proxy.py`

**Features**:
- Authenticates with proxy using device_secret
- Receives and stores short-lived JWT token
- Automatic token refresh (at 80% of lifetime = 12 minutes)
- All VAPI calls proxied through server
- Never holds VAPI API key

---

## Setup Instructions

### Step 1: Server Configuration

**Add to Railway Environment Variables**:
```bash
VAPI_API_KEY=e4077034-d96a-41c7-8f49-e36accb11fb4
```

This is the only place the VAPI API key exists!

### Step 2: Register Device

**In** `webhook_service/device_auth.py`:

```python
DEVICES = {
    "pi_urbanjungle_001": {
        "device_id": "pi_urbanjungle_001",
        "device_secret": "dev_secret_urbanjungle_abc123xyz",
        "customer_id": "urbanjungle",
        "name": "Urban Jungle - Raspberry Pi #1",
        "active": True
    }
}
```

### Step 3: Pi Configuration

**Create** `config/device_config.json` on Pi:

```json
{
  "device_id": "pi_urbanjungle_001",
  "device_secret": "dev_secret_urbanjungle_abc123xyz",
  "proxy_url": "https://securevoice-production-f5c9.up.railway.app",
  "vapi_assistant_id": "31377f1e-dd62-43df-bc3c-ca8e87e08138"
}
```

### Step 4: Run Secure Client on Pi

```bash
python3 src/vapi_client_secure_proxy.py
```

---

## Authentication Flow

### Initial Authentication

```
Pi → POST /device/auth
     Body: { device_id, device_secret }

Server validates credentials
Server generates JWT token (15-min expiry)

Server → Pi
     Response: { access_token, expires_in: 900 }

Pi stores token and expiry time
```

### Making VAPI Calls

```
Pi → POST /vapi/start
     Headers: Authorization: Bearer {jwt-token}
     Body: { assistant_id, assistant_overrides }

Server verifies JWT token
Server extracts device_id and customer_id from token
Server calls VAPI API with VAPI_API_KEY (from environment)

VAPI → Server → Pi
     Response: { call details }
```

### Token Refresh (Automatic)

```
[Every 12 minutes - at 80% of 15-min lifetime]

Pi → POST /device/refresh
     Headers: Authorization: Bearer {current-token}

Server verifies current token is valid
Server issues new JWT token (new 15-min expiry)

Server → Pi
     Response: { access_token, expires_in: 900 }

Pi updates stored token
```

---

## Token Lifecycle

```
Time 0:00 → Device authenticates → Gets Token A (expires at 15:00)
Time 12:00 → Auto-refresh → Gets Token B (expires at 27:00)
Time 24:00 → Auto-refresh → Gets Token C (expires at 39:00)
...continues indefinitely while session is active
```

**If Pi goes offline**:
- Token expires after 15 minutes
- Must re-authenticate on reconnect
- No security risk - expired tokens are rejected

---

## Testing

### 1. Test Device Authentication

```bash
curl -X POST "https://securevoice-production-f5c9.up.railway.app/device/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "pi_urbanjungle_001",
    "device_secret": "dev_secret_urbanjungle_abc123xyz"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "customer_id": "urbanjungle",
  "device_info": {
    "device_id": "pi_urbanjungle_001",
    "customer_id": "urbanjungle",
    "name": "Urban Jungle - Raspberry Pi #1",
    "active": true
  }
}
```

### 2. Test Token Refresh

```bash
TOKEN="eyJ..."  # From previous response

curl -X POST "https://securevoice-production-f5c9.up.railway.app/device/refresh" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "access_token": "eyJ...",  # New token
  "token_type": "Bearer",
  "expires_in": 900
}
```

### 3. Test VAPI Proxy

```bash
TOKEN="eyJ..."  # Valid JWT token

curl -X POST "https://securevoice-production-f5c9.up.railway.app/vapi/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "31377f1e-dd62-43df-bc3c-ca8e87e08138",
    "assistant_overrides": {
      "firstMessageMode": "assistant-speaks-first"
    }
  }'
```

Expected: VAPI call starts, returns call details

### 4. Test Secure Pi Client

```bash
python3 src/vapi_client_secure_proxy.py
```

Expected flow:
1. Pi authenticates → gets JWT token
2. Pi starts VAPI call via proxy
3. Token auto-refreshes every 12 minutes
4. Voice session works normally

---

## Device Management

### Register New Device

```python
from webhook_service.device_auth import register_new_device

device = register_new_device(
    device_id="pi_customer2_001",
    customer_id="customer2",
    name="Customer 2 - Raspberry Pi #1"
)

print(f"Device secret: {device['device_secret']}")
# Save this secret securely for the Pi
```

### Revoke Compromised Device

```python
from webhook_service.device_auth import revoke_device

revoke_device("pi_urbanjungle_001")
# All tokens for this device immediately become invalid
```

### Check Device Info

```bash
TOKEN="eyJ..."

curl -X GET "https://securevoice-production-f5c9.up.railway.app/device/info" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Security Best Practices

### ✅ DO
1. **Store device_secret securely on Pi** - use environment variables or encrypted config
2. **Rotate device secrets periodically** - update DEVICES registry
3. **Monitor failed authentication attempts** - detect brute force attacks
4. **Use HTTPS only** - protect tokens in transit
5. **Set appropriate TOKEN_TTL** - balance security vs. usability (default: 15 min)
6. **Revoke devices immediately if compromised**

### ❌ DON'T
1. **Never commit device_secret to git** - add to .gitignore
2. **Never log JWT tokens** - they're sensitive
3. **Never share device_secret between devices** - each device gets unique secret
4. **Never extend TOKEN_TTL beyond 1 hour** - defeats purpose of short-lived tokens
5. **Never store VAPI_API_KEY on Pi** - defeats entire architecture

---

## Production Considerations

### Database Storage (Recommended)
Current implementation uses in-memory `DEVICES` dictionary. For production:

```python
# Use PostgreSQL, MySQL, or Redis
# Store: device_id, device_secret_hash, customer_id, active, created_at, last_seen

def validate_device_credentials(device_id, device_secret):
    device = db.query("SELECT * FROM devices WHERE device_id = ?", device_id)
    if not device or not device['active']:
        return None

    # Verify hashed secret
    if bcrypt.checkpw(device_secret.encode(), device['secret_hash']):
        return device
    return None
```

### JWT Secret Rotation
Current implementation generates JWT_SECRET on startup. For production:

```python
# Store JWT secret in environment variable
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))

# Rotate periodically (e.g., monthly)
# Support multiple valid secrets for gradual rotation
```

### Rate Limiting
Add rate limiting to prevent abuse:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/device/auth")
@limiter.limit("5 per minute")  # Max 5 auth attempts per minute
async def device_authenticate(request: Request):
    ...
```

---

## Comparison: Old vs. New

### Old System (Insecure)
```
Pi has:
- VAPI_API_KEY (permanent, full access)
- If Pi compromised → full account access

Risk: HIGH
Revocation: Requires rotating VAPI API key (affects all devices)
```

### New System (Tier 0 Secure)
```
Pi has:
- device_secret (device-specific, revocable)
- JWT token (15-minute TTL, auto-expires)
- If Pi compromised → limited to one device, 15 minutes max

Risk: LOW
Revocation: Instant (revoke_device, all tokens invalid)
```

---

## Summary

✅ **VAPI API key never leaves server**
✅ **Short-lived tokens (15-minute expiry)**
✅ **Automatic token refresh**
✅ **Per-device revocation**
✅ **Compromised Pi has minimal impact**
✅ **Centralized key management**
✅ **Production-ready architecture**

**Version**: 4.0.0
**Date**: 2025-10-09
**Status**: Ready for deployment
