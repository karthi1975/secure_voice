# 🏗️ Architecture Flow - Secure Voice Multi-Tenant System

Complete technical documentation of the secure voice control system with multi-tenant support.

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SECURE VOICE ARCHITECTURE                        │
│                                                                      │
│  Edge Devices (Pi)  →  Railway Proxy  →  VAPI AI  →  Home Assistant │
│                                                                      │
│  Zero Secrets       JWT Auth         Voice AI     Smart Home        │
│  on Edge            Multi-Tenant     Platform     Automation        │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Complete Call Flow - Step by Step

### Phase 1: Client Startup & Authentication

```
┌────────────────────────────────────────────────┐
│ Raspberry Pi (Edge Device)                     │
│ src/vapi_client_sdk.py                         │
└────────────────────────────────────────────────┘
              │
              │ 1. User runs: python src/vapi_client_sdk.py
              │
              ▼
┌────────────────────────────────────────────────┐
│ Step 1: Load Device Config (line 20-30)       │
│                                                │
│ From config/device_config.json:                │
│   device_id: "pi_urbanjungle_001"             │
│   device_secret: "dev_secret_urbanjungle..."  │
│   proxy_url: "https://your-app.railway.app"   │
└────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────┐
│ Step 2: Authenticate with Proxy (line 42-78)  │
│                                                │
│ POST /device/auth                              │
│ Body: {                                        │
│   "device_id": "pi_urbanjungle_001",          │
│   "device_secret": "dev_secret_..."           │
│ }                                              │
└────────────────────────────────────────────────┘
              │
              │ HTTP Request
              ▼
┌────────────────────────────────────────────────┐
│ Railway Server (main.py:161-208)               │
│                                                │
│ • Validates device_id + device_secret          │
│ • Looks up customer_id: "urbanjungle"         │
│ • Generates JWT token (15 min expiry)         │
│ • Returns: {                                   │
│     "access_token": "eyJhbGc...",              │
│     "expires_in": 900,                         │
│     "customer_id": "urbanjungle"               │
│   }                                            │
└────────────────────────────────────────────────┘
              │
              │ JWT Token
              ▼
┌────────────────────────────────────────────────┐
│ Raspberry Pi stores JWT token (line 58)       │
│                                                │
│ ✅ Authentication successful!                  │
│    Customer: urbanjungle                       │
│    Token valid for: 15 minutes                 │
└────────────────────────────────────────────────┘
```

### Phase 2: Fetching VAPI Configuration

```
┌────────────────────────────────────────────────┐
│ Step 3: Request VAPI Config (line 62-78)      │
│                                                │
│ GET /device/vapi-config                        │
│ Headers:                                       │
│   Authorization: Bearer {JWT_TOKEN}            │
└────────────────────────────────────────────────┘
              │
              │ HTTP Request with JWT
              ▼
┌────────────────────────────────────────────────┐
│ Railway Server (main.py:260-287)               │
│                                                │
│ • Validates JWT token                          │
│ • Extracts device_id & customer_id from token  │
│ • Returns VAPI config:                         │
│   {                                            │
│     "api_key": "e4077034-...",                 │
│     "assistant_id": "31377f1e-...",            │
│     "device_id": "pi_urbanjungle_001",         │
│     "customer_id": "urbanjungle"               │
│   }                                            │
└────────────────────────────────────────────────┘
              │
              │ VAPI Config
              ▼
┌────────────────────────────────────────────────┐
│ Raspberry Pi receives config (line 71-78)     │
│                                                │
│ ✅ VAPI config received!                       │
│    API Key: e4077034... (first 20 chars)       │
│    Assistant ID: 31377f1e-...                  │
│                                                │
│ • Initializes VAPI SDK with API key            │
└────────────────────────────────────────────────┘
```

### Phase 3: Starting VAPI Call with serverUrl Override

```
┌────────────────────────────────────────────────┐
│ Step 4: Start VAPI Call (line 96-107)         │
│                                                │
│ Build serverUrl with device_id:                │
│   webhook_url = f"{proxy_url}/webhook?         │
│                  device_id={device_id}"        │
│   webhook_url = "https://your-app.railway.app/ │
│                  webhook?device_id=            │
│                  pi_urbanjungle_001"           │
│                                                │
│ vapi.start(                                    │
│   assistant_id=assistant_id,                   │
│   assistant_overrides={                        │
│     "serverUrl": webhook_url                   │
│   }                                            │
│ )                                              │
└────────────────────────────────────────────────┘
              │
              │ Calls VAPI API
              ▼
┌────────────────────────────────────────────────┐
│ VAPI Cloud Service                             │
│                                                │
│ • Loads assistant: "31377f1e-..."              │
│ • Applies serverUrl override                   │
│ • Returns call object with:                    │
│   - Call ID                                    │
│   - Web call URL (for browser access)          │
│   - WebRTC connection info                     │
└────────────────────────────────────────────────┘
              │
              │ Call started
              ▼
┌────────────────────────────────────────────────┐
│ Raspberry Pi receives call info (line 109-123) │
│                                                │
│ ✅ Voice session started!                      │
│    Call ID: abc-123-def                        │
│    Web Call URL: https://vapi.daily.co/...     │
│                                                │
│ 🔊 Voice session active                        │
│ 🎤 Start speaking to control devices           │
│ ♾️  Will auto-restart on call end              │
└────────────────────────────────────────────────┘
```

### Phase 4: User Speaks to VAPI Assistant

```
┌────────────────────────────────────────────────┐
│ User says: "Turn on the fan"                   │
└────────────────────────────────────────────────┘
              │
              │ Audio stream
              ▼
┌────────────────────────────────────────────────┐
│ VAPI Voice AI Platform                         │
│                                                │
│ 1. Speech-to-Text: "Turn on the fan"           │
│                                                │
│ 2. Loads System Prompt:                        │
│    "You are Luna, a voice assistant for        │
│     smart home control..."                     │
│                                                │
│ 3. Loads Function Definitions:                 │
│    {                                           │
│      "name": "control_air_circulator",         │
│      "description": "Control air circulator",  │
│      "parameters": {                           │
│        "device": "power|speed|oscillation",    │
│        "action": "turn_on|turn_off|low|..."    │
│      }                                         │
│    }                                           │
│                                                │
│ 4. LLM (Language Model) processes:             │
│    Input: "Turn on the fan"                    │
│    Decision: Call control_air_circulator with: │
│              device="power", action="turn_on"  │
└────────────────────────────────────────────────┘
              │
              │ Function call decision
              ▼
┌────────────────────────────────────────────────┐
│ VAPI sends webhook to serverUrl               │
│                                                │
│ POST /webhook?device_id=pi_urbanjungle_001     │
│                                                │
│ Body: {                                        │
│   "message": {                                 │
│     "type": "tool-calls",                      │
│     "toolCalls": [{                            │
│       "function": {                            │
│         "name": "control_air_circulator",      │
│         "arguments": {                         │
│           "device": "power",                   │
│           "action": "turn_on"                  │
│         }                                      │
│       }                                        │
│     }]                                         │
│   }                                            │
│ }                                              │
└────────────────────────────────────────────────┘
```

### Phase 5: Multi-Tenant Webhook Routing

```
┌────────────────────────────────────────────────┐
│ Railway Server receives webhook (main.py:458)  │
│                                                │
│ Query param: device_id=pi_urbanjungle_001      │
│                                                │
│ Step 1: device_id → customer_id                │
│   get_customer_id_from_device(                 │
│     "pi_urbanjungle_001"                       │
│   )                                            │
│   → returns: "urbanjungle"                     │
│                                                │
│ Step 2: customer_id → HA instance              │
│   get_ha_instance("urbanjungle")               │
│   → returns: {                                 │
│       "ha_url": "https://ut-demo-urbanjungle.  │
│                  homeadapt.us",                │
│       "ha_webhook_id": "vapi_air_circulator",  │
│       "name": "Urban Jungle Demo"              │
│     }                                          │
│                                                │
│ ✅ Routed: pi_urbanjungle_001 →                │
│           urbanjungle → Urban Jungle Demo      │
└────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────┐
│ Process Function Call (main.py:691-763)        │
│                                                │
│ Function: control_air_circulator               │
│ Arguments: device="power", action="turn_on"    │
│                                                │
│ Build HA webhook URL:                          │
│   ha_url = "https://ut-demo-urbanjungle.       │
│             homeadapt.us"                      │
│   webhook_id = "vapi_air_circulator"           │
│   full_url = f"{ha_url}/api/webhook/           │
│                {webhook_id}"                   │
└────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────┐
│ Forward to Home Assistant (main.py:723-756)    │
│                                                │
│ POST https://ut-demo-urbanjungle.homeadapt.us/ │
│      api/webhook/vapi_air_circulator           │
│                                                │
│ Body: {                                        │
│   "message": {                                 │
│     "toolCalls": [{                            │
│       "function": {                            │
│         "arguments": {                         │
│           "device": "power",                   │
│           "action": "turn_on"                  │
│         }                                      │
│       }                                        │
│     }]                                         │
│   }                                            │
│ }                                              │
└────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────┐
│ Home Assistant (Urban Jungle Demo)             │
│ Automation: HA_AUTOMATION_SIMPLE.yaml          │
│                                                │
│ Trigger: webhook_id = "vapi_air_circulator"    │
│                                                │
│ Extract variables:                             │
│   device = trigger.json.message.toolCalls[0].  │
│            function.arguments.device           │
│          = "power"                             │
│   action = trigger.json.message.toolCalls[0].  │
│            function.arguments.action           │
│          = "turn_on"                           │
│                                                │
│ Condition matches: device=="power" AND         │
│                    action=="turn_on"           │
│                                                │
│ Execute action:                                │
│   service: fan.turn_on                         │
│   target:                                      │
│     entity_id: fan.air_circulator              │
│                                                │
│ 🌀 FAN TURNS ON! 🌀                            │
└────────────────────────────────────────────────┘
              │
              │ HTTP 200 OK
              ▼
┌────────────────────────────────────────────────┐
│ Railway Server (main.py:749-756)               │
│                                                │
│ HA returned 200 OK                             │
│ Build result message: "Power turn on"          │
│                                                │
│ Return to VAPI: {                              │
│   "results": [{                                │
│     "type": "function-result",                 │
│     "name": "control_air_circulator",          │
│     "result": "Power turn on"                  │
│   }]                                           │
│ }                                              │
└────────────────────────────────────────────────┘
              │
              │ Function result
              ▼
┌────────────────────────────────────────────────┐
│ VAPI Voice AI Platform                         │
│                                                │
│ Function result received: "Power turn on"      │
│                                                │
│ LLM generates response based on:               │
│   - System prompt (Luna's personality)         │
│   - Function result                            │
│   - User's original request                    │
│                                                │
│ Generated response: "I've turned on the fan    │
│                      for you."                 │
│                                                │
│ Text-to-Speech: Converts to audio              │
└────────────────────────────────────────────────┘
              │
              │ Audio stream
              ▼
┌────────────────────────────────────────────────┐
│ User hears: "I've turned on the fan for you."  │
└────────────────────────────────────────────────┘
```

### Phase 6: Auto-Restart on Call End

```
┌────────────────────────────────────────────────┐
│ Call ends (user hangs up or error)             │
└────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────┐
│ Client detects call end (line 129-140)         │
│                                                │
│ ⚠️  Call ended or error                        │
│ 🔄 Auto-restarting in 3 seconds...            │
│                                                │
│ • Stops current call                           │
│ • Waits 3 seconds                              │
│ • Loops back to Phase 3                        │
│ • Starts new call automatically                │
│                                                │
│ ♾️  Runs forever until Ctrl+C                  │
└────────────────────────────────────────────────┘
```

## 🔑 Key Components

### 1. serverUrl Override

**Critical Line (vapi_client_sdk.py:93-105):**
```python
webhook_url = f"{self.proxy_url}/webhook?device_id={self.device_id}"
assistant_overrides["serverUrl"] = webhook_url
```

**What it does:** Tells VAPI "send all function calls to THIS URL with THIS device_id parameter"

### 2. Multi-Tenant Routing

**Device ID → Customer ID (device_auth.py):**
```python
DEVICES = {
    "pi_urbanjungle_001": {
        "customer_id": "urbanjungle",
        # ...
    }
}
```

**Customer ID → HA Instance (ha_instances.py):**
```python
HA_INSTANCES = {
    "urbanjungle": {
        "ha_url": "https://ut-demo-urbanjungle.homeadapt.us",
        "ha_webhook_id": "vapi_air_circulator",
        "name": "Urban Jungle Demo"
    }
}
```

### 3. JWT Token Security

**Token Generation (device_auth.py:35-48):**
```python
payload = {
    "device_id": device_id,
    "customer_id": customer_id,
    "type": "device_token",
    "iat": current_time,
    "exp": current_time + (TOKEN_TTL_MINUTES * 60)
}
token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
```

**Token Validation (device_auth.py:51-69):**
- Verifies JWT signature
- Checks expiration
- Extracts device_id and customer_id

### 4. VAPI Configuration (System Prompt + Tools)

**System Prompt Example (VAPI_SYSTEM_PROMPT_AIR_CIRCULATOR.txt):**
```
You are Luna, a friendly voice assistant for smart home control.
You help users control their air circulator fan.
Be concise and conversational.
```

**Tool Configuration Example (FRONT_DOOR_TOOL_FOR_VAPI.json):**
```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Control the air circulator fan",
    "parameters": {
      "type": "object",
      "properties": {
        "device": {
          "type": "string",
          "enum": ["power", "speed", "oscillation", "sound"]
        },
        "action": {
          "type": "string",
          "enum": ["turn_on", "turn_off", "low", "medium", "high"]
        }
      }
    }
  }
}
```

## 🔒 Security Model

### Zero Trust Architecture

1. **Edge Device (Pi)**
   - Stores: `device_id`, `device_secret`, `proxy_url`
   - **NEVER stores**: VAPI API key, HA credentials

2. **Railway Proxy**
   - Validates: Device credentials, JWT tokens
   - Holds: VAPI API key, HA instance configs
   - Routes: Based on device_id → customer_id

3. **Communication**
   - All HTTP requests over HTTPS
   - JWT tokens expire after 15 minutes
   - Device secret can be revoked anytime

### Compromise Scenarios

| Compromised | Impact | Mitigation |
|-------------|--------|------------|
| Pi Device | ✅ Minimal - only device_secret exposed | Revoke device_secret in server config |
| Railway Server | ⚠️ High - VAPI key exposed | Rotate VAPI key, update server |
| VAPI Account | ⚠️ High - voice calls compromised | Rotate VAPI key |
| HA Instance | ⚠️ Medium - one customer affected | Customer-specific mitigation |

## 📈 Scalability

### Adding New Tenants

**Steps:**
1. Add device to `device_auth.py`
2. Add HA instance to `ha_instances.py`
3. Deploy changes to Railway
4. Configure Pi with new credentials

**Capacity:**
- Devices per server: 1000s (limited by Railway resources)
- Customers per server: 100s (limited by HA routing logic)
- Calls per device: Unlimited (auto-restart)

## 🔍 Monitoring & Debugging

### Railway Logs

**Key log messages:**
```
✅ Device authenticated: pi_xxx → customer: yyy
📡 VAPI config requested by device: pi_xxx
✅ Routed via device_id: pi_xxx → customer: yyy → HA: zzz
🏠 Using HA for customer: https://...
🌀 FAN TURNS ON! (in HA logs)
```

### Health Checks

- **Railway**: `GET /health`
- **VAPI**: Check dashboard for call logs
- **HA**: Check webhook automation triggers

## 🎯 Summary

The serverUrl override with device_id parameter is the key innovation that enables:
- ✅ Multi-tenant routing
- ✅ Zero secrets on edge devices
- ✅ Scalable architecture
- ✅ Easy customer onboarding
- ✅ Centralized configuration management

All while maintaining security and enabling 24/7 operation with auto-restart!
