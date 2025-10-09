# Authenticated VAPI Setup Guide

This guide shows how to set up VAPI with session-based authentication.

## Overview

The authenticated flow requires users to log in before controlling devices:

1. User connects to VAPI
2. Assistant calls `home_auth()` function
3. Server validates credentials from session
4. After authentication, user can control devices via `control_air_circulator()`

## Setup Steps

### 1. Create Session on Server

The client creates a session with credentials before starting the call:

```python
python src/vapi_client_with_auth.py
```

This will:
- Create a session with customer_id and password
- Get a session ID (sid)
- Start VAPI call with `serverUrl` including the sid

### 2. Configure VAPI Assistant

In VAPI Dashboard, update your assistant with:

**System Prompt** (from `config/AUTHENTICATED_PROMPT.txt`):

```
You are Luna, a voice-controlled smart home assistant.

AUTHENTICATION REQUIRED: Users must authenticate before controlling devices.

YOUR JOB:
1. First call home_auth() to authenticate the user
2. After successful authentication, control devices using control_air_circulator()

[... rest of prompt ...]
```

### 3. Configure Tools in VAPI

Add TWO tools to your assistant:

#### Tool 1: home_auth (Authentication)

```json
{
  "type": "function",
  "function": {
    "name": "home_auth",
    "description": "Authenticate the user before allowing device control. Must be called first.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  "server": {
    "url": "https://securevoice-production-eb77.up.railway.app/webhook?sid={{DYNAMIC_SID}}"
  },
  "messages": [
    {
      "type": "request-start",
      "blocking": true
    }
  ]
}
```

**Note**: The `sid` parameter is dynamically added by the client using `serverUrl` override.

#### Tool 2: control_air_circulator (Device Control)

```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Control air circulator - power, speed, oscillation, and sound. Only call after successful authentication.",
    "parameters": {
      "type": "object",
      "properties": {
        "device": {
          "type": "string",
          "enum": ["power", "speed", "oscillation", "sound"],
          "description": "Which device feature to control: power, speed, oscillation, or sound"
        },
        "action": {
          "type": "string",
          "enum": ["turn_on", "turn_off", "low", "medium", "high"],
          "description": "Action to perform: turn_on, turn_off, low, medium, or high"
        }
      },
      "required": ["device", "action"]
    }
  },
  "server": {
    "url": "https://securevoice-production-eb77.up.railway.app/webhook?sid={{DYNAMIC_SID}}"
  }
}
```

### 4. Test the Flow

Run the authenticated client:

```bash
python src/vapi_client_with_auth.py
```

**Expected Flow:**

1. Client creates session and gets `sid`
2. Client starts VAPI call with `serverUrl` including `?sid=xxx`
3. User connects to call
4. Assistant automatically calls `home_auth()`
5. Server validates credentials from session
6. On success, user can say "Turn on the fan"
7. Assistant calls `control_air_circulator(device="power", action="turn_on")`
8. Server checks authentication, forwards to Home Assistant
9. Fan turns on

## Configuration

Edit `config/config.json`:

```json
{
  "customer_id": "urbanjungle",
  "password": "alpha-bravo-123",
  "vapi_assistant_id": "your-assistant-id",
  "vapi_api_key": "your-api-key",
  "server_url": "https://securevoice-production-eb77.up.railway.app",
  "homeassistant_url": "https://ut-demo-urbanjungle.homeadapt.us"
}
```

## Security Features

1. **Session-based authentication**: Credentials stored in server-side session
2. **24-hour session timeout**: Sessions expire after 24 hours
3. **Per-call authentication**: Each VAPI call must authenticate
4. **Function-level checks**: Device control only allowed after authentication

## Troubleshooting

### Authentication fails

- Check credentials in `config/config.json`
- Verify session was created (check logs)
- Ensure `sid` parameter is in webhook URL

### Device control doesn't work

- Ensure authentication succeeded first
- Check Railway logs for authentication status
- Verify both tools are configured in VAPI

### Session expired

- Sessions last 24 hours
- Restart the client to create a new session
- Check server logs for session expiration messages

## API Endpoints

- `POST /sessions` - Create new session with credentials
- `POST /webhook?sid=xxx` - Unified webhook for auth and control
- `POST /auth?sid=xxx` - Authentication endpoint (called by webhook)
- `POST /control?sid=xxx` - Device control endpoint (called by webhook)

## Next Steps

After testing authentication:

1. Implement secure credential storage (not in JSON file)
2. Add user registration/management
3. Implement Redis for session storage (currently in-memory)
4. Add session refresh mechanism
5. Implement logout functionality
