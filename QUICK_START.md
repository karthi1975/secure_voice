# 🚀 Quick Start - Voice Controlled Fan

## ✅ What's Working
- Voice authentication
- Direct webhook control of fan (tested and confirmed)
- Railway deployment
- Home Assistant integration

## 🔧 Final Configuration Steps

### Step 1: Update Home Assistant Automation (5 minutes)

1. Open Home Assistant: https://ut-demo-urbanjungle.homeadapt.us
2. Go to **Settings → Automations**
3. Find **"VAPI - Air Circulator Control"**
4. Click **︙ menu → Edit in YAML**
5. **Delete all content** and paste from `WORKING_AUTOMATION.yaml`
6. Click **Save**

**File to copy**: `/Users/karthi/business/tetradapt/secure_voice/WORKING_AUTOMATION.yaml`

### Step 2: Update VAPI System Prompt (5 minutes)

1. Go to https://vapi.ai/dashboard
2. Find assistant: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
3. Click **Edit**
4. Find **System Prompt** section
5. **Replace entire prompt** with content from `config/FUNCTION_CALLING_PROMPT.txt`
6. Click **Save**

**File to copy**: `/Users/karthi/business/tetradapt/secure_voice/config/FUNCTION_CALLING_PROMPT.txt`

### Step 3: Verify VAPI Tools (2 minutes)

In the same VAPI assistant settings:

1. Go to **Tools** section
2. Check `home_auth` tool:
   - Should have NO `server.url` field
   - Or `server.url` should be empty/deleted
3. Check `control_air_circulator` tool:
   - Should have NO `server.url` field
   - Or `server.url` should be empty/deleted

**Why?** Individual tool URLs override the client's dynamic serverUrl, breaking session auth.

## 🎤 Testing End-to-End

After completing the 3 steps above:

```bash
# Start the voice client
cd /Users/karthi/business/tetradapt/secure_voice
source venv/bin/activate
python src/vapi_client_clean.py
```

### Test Conversation

1. **You say**: "Luna"
2. **Luna says**: "Authentication successful"
3. **You say**: "Turn on the fan"
4. **Luna says**: "Fan is on"
5. **Physical fan should turn ON** ✅

6. **You say**: "Turn off the fan"
7. **Luna says**: "Fan is off"
8. **Physical fan should turn OFF** ✅

## 🔍 Troubleshooting

### If fan doesn't turn on after voice command:

**Check 1: Did Luna call the function?**
Look at the terminal output - you should see:
```
Function call: control_air_circulator
Parameters: {"device": "power", "action": "turn_on"}
```

If you DON'T see this → **VAPI system prompt not updated** (go back to Step 2)

**Check 2: Did Home Assistant receive the webhook?**
1. Open Home Assistant
2. Settings → Automations → VAPI - Air Circulator Control
3. Click ︙ menu → **Traces**
4. Check the latest trace

If trace shows error → **Home Assistant automation not updated** (go back to Step 1)

**Check 3: Is the entity working?**
Test directly in Home Assistant:
1. Go to Settings → Devices & Services → Devices
2. Find "Air Circulator"
3. Click on it
4. Try toggling the fan manually

If manual toggle doesn't work → **Device/entity issue** (not related to VAPI)

## 📋 Quick Reference

### VAPI Configuration
- **Assistant ID**: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
- **Webhook**: `https://securevoice-production.up.railway.app/webhook?sid=xxx`
- **Tools**: `home_auth`, `control_air_circulator`

### Home Assistant
- **URL**: `https://ut-demo-urbanjungle.homeadapt.us`
- **Webhook ID**: `vapi_air_circulator`
- **Entity**: `fan.air_circulator`

### Supported Voice Commands
- "Turn on the fan" / "Turn off the fan"
- "Set to low" / "Set to medium" / "Set to high"
- "Turn on oscillation" / "Turn off oscillation"
- "Turn on sound" / "Turn off sound"

## 📊 System Status

✅ Railway webhook deployed
✅ GitHub repository clean (no secrets)
✅ Direct webhook test working
⏳ VAPI system prompt (needs update)
⏳ Home Assistant automation (needs update)

## 📞 Support Files

- **Deployment docs**: `DEPLOYMENT_COMPLETE.md`
- **Working automation**: `WORKING_AUTOMATION.yaml`
- **System prompt**: `config/FUNCTION_CALLING_PROMPT.txt`
- **Test scripts**: `test_ha_direct.py`, `test_after_restart.sh`

---

**Next Step**: Complete Steps 1-3 above, then run the end-to-end test!
