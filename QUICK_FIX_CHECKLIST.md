# Quick Fix Checklist - Get Luna Working Now

## 🎯 The Problem
Voice authentication works, but commands like "turn on fan" don't work.

## 🔧 The Fix (5 Steps)

### Step 1: Update VAPI System Prompt
1. Go to VAPI dashboard: https://vapi.ai
2. Open assistant: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
3. Delete current system prompt
4. Copy from `/config/CURRENT_SYSTEM_PROMPT.md`
5. Paste into VAPI
6. Save

**Must start with:** "On your VERY FIRST response: 1. Call home_auth()"

### Step 2: Fix home_auth Tool
1. In VAPI assistant, go to Tools/Functions
2. Delete existing `home_auth` tool
3. Add new tool with this JSON:

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

**CRITICAL**: Do NOT add `server` or `server.url` field!

### Step 3: Fix control_air_circulator Tool
1. In VAPI assistant, go to Tools/Functions
2. Delete existing `control_air_circulator` tool
3. Add new tool with this JSON:

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

**CRITICAL**: Do NOT add `server` or `server.url` field!

### Step 4: Clear First Message
1. In VAPI assistant settings
2. Find "First Message" field
3. Clear it (make it empty)
4. Save

### Step 5: Test
```bash
cd /Users/karthi/business/tetradapt/secure_voice
python3 src/vapi_client_clean.py
```

Wait for Luna to say: "Welcome! Authentication successful..."

Then say: "Hey Luna, turn on the fan"

## ✅ Expected Result
Luna should respond: "Fan on"

## ❌ If Still Not Working

Check Railway logs:
```bash
railway logs
```

Look for:
- Session creation with sid
- home_auth function call
- control_air_circulator function call

## 📝 Why This Works

**Before:**
- Tools had individual `server.url` that overrode client's `serverUrl`
- System prompt didn't call `home_auth()` on first turn
- Old password-based authentication approach

**After:**
- Tools have NO `server.url` - client's `serverUrl` with sid routes everything
- System prompt explicitly calls `home_auth()` on first turn
- Session-based authentication with proper routing

## 🔗 Full Documentation
- Complete guide: `/VAPI_CONFIGURATION_GUIDE.md`
- Debug steps: `/DEBUG_WEBHOOK_TEST.md`
- Fix summary: `/FIX_SUMMARY.md`
