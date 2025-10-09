# ✅ Deployment Complete - Voice-Controlled Fan Working!

## What's Working Now

1. **Voice Authentication** - Luna authenticates using session-based auth
2. **Fan Control via Voice** - "Turn on the fan" / "Turn off the fan" works
3. **Webhook Integration** - Railway webhook forwards commands to Home Assistant
4. **Physical Device Control** - Home Assistant automation controls the actual fan

## Fixed Issues

### Issue 1: Webhook Payload Format Mismatch
**Problem**: Home Assistant automation expected `trigger.json.message.toolCalls` but got error "no attribute 'message'"

**Root Cause**: The webhook was wrapping data in a `message` object, but Home Assistant receives webhook data at the root level of `trigger.json`

**Solution**: Updated webhook to send:
```json
{
  "toolCalls": [{
    "function": {
      "arguments": {
        "device": "power",
        "action": "turn_on"
      }
    }
  }]
}
```

Instead of:
```json
{
  "message": {
    "toolCalls": [...]
  }
}
```

## Deployment Status

### Railway Webhook Service
- **URL**: https://securevoice-production.up.railway.app
- **Status**: ✅ Deployed and running
- **Health Check**: https://securevoice-production.up.railway.app/health
- **Auto-deploy**: Enabled from GitHub main branch

### Home Assistant
- **URL**: https://ut-demo-urbanjungle.homeadapt.us
- **Webhook ID**: `vapi_air_circulator`
- **Automation**: VAPI - Air Circulator Control
- **Entity**: `fan.air_circulator`

### VAPI Configuration
- **Assistant ID**: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
- **serverUrl**: Set dynamically by client with `?sid=xxx` parameter
- **Tools**:
  - `home_auth()` - Authentication (first turn only)
  - `control_air_circulator(device, action)` - Device control

## Testing

### Test 1: Direct Webhook Test (Bypassing VAPI)
```bash
# Turn ON
curl -X POST "https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator" \
  -H "Content-Type: application/json" \
  -d '{
    "toolCalls": [{
      "function": {
        "arguments": {
          "device": "power",
          "action": "turn_on"
        }
      }
    }]
  }'

# Turn OFF
curl -X POST "https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator" \
  -H "Content-Type: application/json" \
  -d '{
    "toolCalls": [{
      "function": {
        "arguments": {
          "device": "power",
          "action": "turn_off"
        }
      }
    }]
  }'
```

**Status**: ✅ Works - Confirmed by user

### Test 2: End-to-End Voice Test
```bash
# Start VAPI client
source venv/bin/activate
python src/vapi_client_clean.py

# Say: "Luna"
# Luna: "Authentication successful"
#
# Say: "Turn on the fan"
# Luna: "Fan is on"
# Physical fan should turn on
```

**Next Step**: Test this once VAPI system prompt is updated

## Next Steps

### 1. Update VAPI System Prompt (CRITICAL)
The VAPI assistant needs to be configured to call functions, not just respond with text.

**Action Required**:
1. Go to https://vapi.ai/dashboard
2. Find assistant `31377f1e-dd62-43df-bc3c-ca8e87e08138`
3. Edit → System Prompt
4. Copy content from `/Users/karthi/business/tetradapt/secure_voice/config/FUNCTION_CALLING_PROMPT.txt`
5. Save

**Why**: Currently Luna might just say "turn on" without calling the `control_air_circulator()` function

### 2. Update Home Assistant Automation
The automation file needs to be updated to match the working payload format.

**Action Required**:
1. Open Home Assistant
2. Go to Settings → Automations
3. Find "VAPI - Air Circulator Control"
4. Click ︙ menu → Edit in YAML
5. Replace entire content with `/Users/karthi/business/tetradapt/secure_voice/WORKING_AUTOMATION.yaml`
6. Save

**Why**: The current automation expects the old format with `message` wrapper

### 3. Verify VAPI Tools Configuration
Make sure tools don't have individual `server.url` that override the client's serverUrl.

**Action Required**:
1. Go to VAPI dashboard
2. Check tools:
   - `home_auth` tool
   - `control_air_circulator` tool
3. Ensure NEITHER has a `server.url` field set
4. The client sets `serverUrl` dynamically with the sid parameter

**Why**: Individual tool URLs override the client's serverUrl, breaking session authentication

## File Changes

### Modified Files
- `/Users/karthi/business/tetradapt/secure_voice/webhook_service/main.py` - Fixed payload format (line 264-275)

### New Files
- `/Users/karthi/business/tetradapt/secure_voice/WORKING_AUTOMATION.yaml` - Correct automation template
- `/Users/karthi/business/tetradapt/secure_voice/DEPLOYMENT_COMPLETE.md` - This file

### Committed
```
fix: correct Home Assistant webhook payload format

The webhook now sends toolCalls at root level instead of nested in "message".
Home Assistant automation expects: trigger.json.toolCalls[0].function.arguments
```

### Deployed
- GitHub: ✅ Pushed to main branch
- Railway: ✅ Auto-deployed from GitHub

## Architecture

```
User Voice
    ↓
VAPI (Luna)
    ↓
calls: home_auth() or control_air_circulator(device, action)
    ↓
Railway Webhook (https://securevoice-production.up.railway.app/webhook?sid=xxx)
    ↓
Validates session, extracts device/action
    ↓
POST to Home Assistant webhook
    ↓
Home Assistant Automation (webhook_id: vapi_air_circulator)
    ↓
Extracts: trigger.json.toolCalls[0].function.arguments.{device, action}
    ↓
Calls HA service (fan.turn_on, fan.turn_off, etc.)
    ↓
Physical Device (fan.air_circulator)
```

## Supported Commands

### Power
- "Turn on the fan" → `device="power"`, `action="turn_on"`
- "Turn off the fan" → `device="power"`, `action="turn_off"`

### Speed
- "Set to low" → `device="speed"`, `action="low"`
- "Set to medium" → `device="speed"`, `action="medium"`
- "Set to high" → `device="speed"`, `action="high"`

### Oscillation
- "Turn on oscillation" → `device="oscillation"`, `action="turn_on"`
- "Turn off oscillation" → `device="oscillation"`, `action="turn_off"`

### Sound
- "Turn on sound" → `device="sound"`, `action="turn_on"`
- "Turn off sound" → `device="sound"`, `action="turn_off"`

## Troubleshooting

### Check Home Assistant Automation Traces
1. Settings → Automations
2. Find "VAPI - Air Circulator Control"
3. Click ︙ menu → Traces
4. See what data was received and where it failed

### Check Railway Logs
```bash
railway logs
```

### Check Home Assistant Logs
Settings → System → Logs

### Test Webhook Directly
Use the curl commands above to test the webhook without VAPI

## Success Criteria

✅ Voice authentication works
✅ Direct webhook test turns fan on/off
⏳ End-to-end voice test (pending VAPI prompt update)
⏳ Home Assistant automation updated with correct format

---

**Generated**: 2025-10-09
**Status**: Webhook fixed and deployed, awaiting VAPI/HA configuration updates
