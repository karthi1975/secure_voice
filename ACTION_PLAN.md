# Action Plan - Fix Luna Voice Assistant

## ✅ What's Already Working
- ✅ Home Assistant automation is configured correctly
- ✅ Webhook service is deployed to Railway
- ✅ Client creates sessions with sid
- ✅ home_auth authentication works

## ❌ What's Not Working
- ❌ Commands like "turn on fan" don't execute
- ❌ VAPI system prompt needs adjustment

## 🔧 Fix Required (3 Steps - 5 Minutes)

### Step 1: Update VAPI System Prompt (2 min)

1. Go to: https://vapi.ai/dashboard
2. Open assistant: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
3. Click "Edit"
4. Go to "System Prompt" section
5. **DELETE** current prompt
6. **COPY** from: `/Users/karthi/business/tetradapt/secure_voice/COPY_TO_VAPI.txt`
7. **PASTE** into VAPI
8. Click "Save"

**Key requirement:** Prompt MUST start with:
```
On your VERY FIRST response:
1. Immediately call home_auth() with no parameters
```

### Step 2: Verify Tool Configuration (2 min)

In VAPI assistant, verify these 2 tools exist:

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
    "description": "Controls the air circulator fan. Only call AFTER authentication.",
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
      },
      "required": ["device", "action"]
    }
  }
}
```

**CRITICAL:**
- ❌ Do NOT add `server` or `server.url` to these tools
- ✅ Let client's `serverUrl` handle routing

### Step 3: Test (1 min)

```bash
cd /Users/karthi/business/tetradapt/secure_voice
python3 src/vapi_client_clean.py
```

**Expected flow:**
1. Client creates session → gets sid
2. Luna says: "Welcome! Authentication successful..."
3. You say: "Hey Luna, turn on the fan"
4. Luna says: "Fan on"
5. Fan actually turns on in Home Assistant

## 🐛 If Still Not Working

### Debug Step 1: Check VAPI Logs
1. Go to VAPI dashboard
2. Click on recent call
3. Check if `home_auth()` was called on first turn
4. Check if `control_air_circulator()` was called for commands

### Debug Step 2: Check Railway Logs
```bash
railway logs
```

Look for:
- `POST /sessions` - session creation
- `POST /webhook?sid=xxx` - function calls
- Function name routing (home_auth vs control_air_circulator)

### Debug Step 3: Check Home Assistant Logs
1. Go to Home Assistant
2. Settings → System → Logs
3. Look for: "VAPI - device: power, action: turn_on"

### Debug Step 4: Manual Webhook Test
```bash
# Create session
SID=$(curl -s -X POST https://securevoice-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "urbanjungle", "password": "alpha-bravo-123"}' | jq -r '.sid')

echo "Session ID: $SID"

# Test home_auth
curl -X POST "https://securevoice-production.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "home_auth",
        "parameters": {}
      }
    }
  }'

# Test control
curl -X POST "https://securevoice-production.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "control_air_circulator",
        "parameters": {
          "device": "power",
          "action": "turn_on"
        }
      }
    }
  }'
```

## 📁 Reference Files

- System Prompt (copy this): `/COPY_TO_VAPI.txt`
- Full System Prompt: `/config/FINAL_SYSTEM_PROMPT.md`
- Tool Definitions: `/config/home_auth_tool.json`, `/config/control_air_circulator_tool.json`
- Client Code: `/src/vapi_client_clean.py`
- Webhook Code: `/webhook_service/main.py`

## 🎯 Success Criteria

When working correctly:
1. ✅ Luna greets you automatically
2. ✅ "Hey Luna, turn on the fan" → Fan turns on
3. ✅ "Set to medium" → Speed changes to medium
4. ✅ "Turn on oscillation" → Fan starts oscillating
5. ✅ "Mute" → Sound turns off

All without any password prompts or authentication errors!
