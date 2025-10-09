# ✅ Working Setup - Voice Controlled Fan

## 🎉 Status: WORKING!

Voice control is now functional. User can say "Turn on the fan" and it works!

## 🏗️ Architecture

```
User Voice
    ↓
VAPI (Luna)
    ↓
Direct server URL configured in tool
    ↓
Home Assistant Webhook
    ↓
Home Assistant Automation (vapi_air_circulator)
    ↓
Physical Fan Device
```

## 📋 Working Configuration

### VAPI Assistant
- **Assistant ID**: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
- **System Prompt**: From `config/SIMPLE_PROMPT.txt`
- **First Message Mode**: "Assistant waits for user"
- **Model**: GPT-4 or GPT-4o
- **Tool Choice**: auto

### VAPI Tool Configuration
**Tool**: `control_air_circulator`
- **Function definition**: From `config/SIMPLE_TOOL_FOR_VAPI.json`
- **Server URL**: `https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator`
- **Description**: "Control the air circulator fan"
- **Parameters**: device, action

### Home Assistant
- **URL**: `https://ut-demo-urbanjungle.homeadapt.us`
- **Webhook ID**: `vapi_air_circulator`
- **Automation**: From `WORKING_AUTOMATION.yaml`
- **Entity**: `fan.air_circulator`

### Client
- **File**: `src/vapi_client_simple.py`
- **Config**: `config/config.json`
- **No authentication** (direct connection)

## 🎤 Supported Voice Commands

### Power Control
- "Turn on the fan"
- "Turn off the fan"
- "Turn on" / "Turn off"
- "Start the fan" / "Stop the fan"

### Speed Control
- "Set to low" / "Low speed"
- "Set to medium" / "Medium speed"
- "Set to high" / "High speed"

## 🚀 How to Use

### Start Voice Session
```bash
python src/vapi_client_simple.py
```

### Speak Commands
1. Start client (above command)
2. Say: "Turn on the fan"
3. Fan turns on! ✅

## 📁 Key Files

### Working Files
- `src/vapi_client_simple.py` - Simple VAPI client
- `config/SIMPLE_PROMPT.txt` - System prompt for VAPI
- `config/SIMPLE_TOOL_FOR_VAPI.json` - Tool configuration
- `WORKING_AUTOMATION.yaml` - Home Assistant automation

### Configuration
- `config/config.json` - VAPI credentials and URLs

## 🔧 Troubleshooting

### If Voice Control Stops Working

**Check 1: VAPI Tool**
- Verify server URL is set: `https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator`
- Verify tool is attached to assistant

**Check 2: Home Assistant**
- Check automation is enabled
- Check webhook ID matches: `vapi_air_circulator`
- Test with curl:
```bash
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
```

**Check 3: VAPI Configuration**
- System prompt updated from `SIMPLE_PROMPT.txt`
- Tool Choice set to "auto"
- Model is GPT-4 or GPT-4o (not GPT-3.5)

## 🔐 Security

**Current Setup**: Direct connection, no authentication

**Security Level**: ⚠️ Medium
- Home Assistant webhook is publicly accessible
- Anyone with the URL can control devices
- OK for home use if behind firewall
- NOT recommended for production/commercial use

**To Add Authentication**: Use the Railway webhook setup with session-based auth (in `vapi_client_clean.py`)

## 📊 Testing

### Quick Test
```bash
# Start client
python src/vapi_client_simple.py

# Say: "Turn on the fan"
# Expected: Fan turns ON

# Say: "Turn off the fan"
# Expected: Fan turns OFF
```

### Direct Webhook Test
```bash
# Turn ON
curl -X POST "https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator" \
  -H "Content-Type: application/json" \
  -d '{"toolCalls":[{"function":{"arguments":{"device":"power","action":"turn_on"}}}]}'

# Turn OFF
curl -X POST "https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator" \
  -H "Content-Type: application/json" \
  -d '{"toolCalls":[{"function":{"arguments":{"device":"power","action":"turn_off"}}}]}'
```

## 🎯 Success Criteria

✅ Voice client connects to VAPI
✅ User says "Turn on the fan"
✅ VAPI calls `control_air_circulator()` function
✅ Home Assistant receives webhook call
✅ Automation extracts device/action
✅ Physical fan turns ON
✅ User says "Turn off the fan"
✅ Physical fan turns OFF

## 📝 Notes

- **Working as of**: 2025-10-09
- **Setup type**: Simple/Direct (no authentication)
- **VAPI approach**: Server URL configured in tool
- **Previous attempts**: Tried dynamic serverUrl override (didn't work)
- **Final solution**: Direct server URL in VAPI tool configuration

---

**Status**: ✅ FULLY OPERATIONAL
