# VAPI Configuration Guide - Session-Based Authentication

This guide shows you how to configure your VAPI assistant for session-based authentication with the Luna smart home voice assistant.

## Architecture Overview

```
Client (vapi_client_clean.py)
    ↓ Creates session
Server (/sessions) → Returns sid
    ↓
Client starts VAPI with serverUrl=".../webhook?sid=xxx"
    ↓
VAPI routes ALL tool calls → /webhook?sid=xxx
    ↓
Webhook routes by function name:
    - home_auth → authenticate()
    - control_air_circulator → control_device()
```

## Step 1: Configure VAPI Assistant

Go to your VAPI dashboard for assistant: `31377f1e-dd62-43df-bc3c-ca8e87e08138`

### 1.1 System Prompt

Copy this **EXACT** system prompt into VAPI:

```
You are Luna, a smart home voice assistant.

## FIRST TURN ONLY - Authentication

On your VERY FIRST response:
1. Call home_auth() immediately - no parameters needed
2. Say EXACTLY what the tool returns
3. NEVER call home_auth() again for the rest of the conversation

## After Authentication - Process Commands

For all commands after authentication:
1. Listen for wake words: "Hey Luna", "Luna", or "Hello Luna"
2. Parse the command to identify device and action
3. Call control_air_circulator(device, action)
4. Respond briefly with confirmation

## Tools Available

### home_auth()
- Call ONCE at conversation start
- No parameters required
- Returns authentication status

### control_air_circulator(device, action)
- Controls the air circulator fan
- **Devices**: power, speed, oscillation, sound
- **Actions**: turn_on, turn_off, low, medium, high

## Response Format

Keep responses under 5 words - be direct and clear.

## Examples

### Turn 1 (Authentication - Automatic)
**System starts conversation**
→ Call: home_auth()
→ Tool returns: "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"
→ Say: "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"

### Turn 2+ (Commands)

**User: "Hey Luna, turn on the fan"**
→ Wake word detected: "Hey Luna" ✓
→ Command: "turn on the fan"
→ Call: control_air_circulator(device="power", action="turn_on")
→ Tool returns: "Power turn on"
→ Say: "Fan on"

**User: "Luna, set to medium"**
→ Wake word detected: "Luna" ✓
→ Command: "set to medium"
→ Call: control_air_circulator(device="speed", action="medium")
→ Tool returns: "Speed medium"
→ Say: "Speed medium"

**User: "Turn on oscillation"**
→ No wake word (command is clear)
→ Command: "Turn on oscillation"
→ Call: control_air_circulator(device="oscillation", action="turn_on")
→ Tool returns: "Oscillation turn on"
→ Say: "Oscillation on"

## Critical Rules

1. **ALWAYS call home_auth() on turn 1** - This is automatic, before any user speech
2. **After turn 1, ONLY call control_air_circulator** - NEVER call home_auth() again
3. Keep responses under 5 words
4. If user speaks before turn 1 completes, say "Please wait"
5. Wake words are optional - parse commands directly if clear
6. Be conversational but brief

## Error Handling

- Unknown command: "Can't do that"
- Unclear request: "Which setting?"
- Network error: "Connection failed"
```

### 1.2 Configure Tools

Add these TWO tools to your VAPI assistant:

**Tool 1: home_auth**
```json
{
  "type": "function",
  "function": {
    "name": "home_auth",
    "description": "Authenticates the session. Call this with no parameters at the start of the conversation.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
```

**Tool 2: control_air_circulator**
```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Controls the air circulator fan (power, speed, oscillation, sound). Only call AFTER authentication completes.",
    "parameters": {
      "type": "object",
      "properties": {
        "device": {
          "description": "Which device feature to control: power, speed, oscillation, or sound",
          "type": "string",
          "enum": [
            "power",
            "speed",
            "oscillation",
            "sound"
          ]
        },
        "action": {
          "description": "Action to perform: turn_on, turn_off, low, medium, or high",
          "type": "string",
          "enum": [
            "turn_on",
            "turn_off",
            "low",
            "medium",
            "high"
          ]
        }
      },
      "required": [
        "device",
        "action"
      ]
    }
  }
}
```

**IMPORTANT**:
- DO NOT add a `server.url` field to these tools
- The `serverUrl` will be set dynamically by the client with the sid parameter

### 1.3 Assistant Settings

In VAPI Assistant Settings:
- **First Message**: Leave EMPTY (home_auth will provide it)
- **Voice**: Choose your preferred voice
- **Model**: gpt-4 or similar (needs function calling)
- **Server URL**: Leave empty (client overrides this)

## Step 2: Verify Webhook is Running

Check your Railway deployment:

```bash
curl https://securevoice-production.up.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

## Step 3: Test Session Creation

```bash
curl -X POST https://securevoice-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "urbanjungle", "password": "alpha-bravo-123"}'
```

Expected response:
```json
{"sid": "some-uuid", "authenticated": false}
```

## Step 4: Run the Client

```bash
cd /Users/karthi/business/tetradapt/secure_voice
python3 src/vapi_client_clean.py
```

## Expected Flow

1. **Client starts**:
   - Creates session → gets sid
   - Starts VAPI with `serverUrl=".../webhook?sid=xxx"`

2. **VAPI calls home_auth()**:
   - POST to `/webhook?sid=xxx` with function-call message
   - Webhook authenticates session
   - Returns: "Welcome! Authentication successful..."

3. **User says: "Hey Luna, turn on the fan"**:
   - VAPI calls `control_air_circulator(device="power", action="turn_on")`
   - POST to `/webhook?sid=xxx` with function-call message
   - Webhook checks authentication, executes control
   - Returns: "Power turn on"

## Troubleshooting

### Issue: Authentication doesn't work
- Check VAPI system prompt has "Call home_auth() immediately" at top
- Verify tools don't have individual `server.url` fields
- Check Railway logs for incoming requests

### Issue: Fan control doesn't work
- Verify authentication completed first
- Check function call has correct parameters (device, action)
- Check Railway logs for the control request

### Issue: VAPI doesn't call home_auth on first turn
- Verify system prompt starts with "On your VERY FIRST response: 1. Call home_auth()"
- Try adding to First Message in VAPI: "{{home_auth()}}"
- Check VAPI logs for function calls

## Files Reference

- System Prompt: `/config/CURRENT_SYSTEM_PROMPT.md`
- home_auth Tool: `/config/home_auth_tool.json`
- control_air_circulator Tool: `/config/control_air_circulator_tool.json`
- Client: `/src/vapi_client_clean.py`
- Webhook: `/webhook_service/main.py`

## Next Steps

Once working:
1. Add more devices (lights, locks, etc.)
2. Implement actual device control (replace simulation)
3. Add session cleanup (expire old sessions)
4. Use Redis for production session storage
