# 🔧 VAPI Configuration - Final Checklist

## ✅ Confirmed Working
- Webhook service: Working perfectly
- Authentication function: Working
- Control function: Working
- Home Assistant: Working

## ❌ Problem
VAPI calls `home_auth()` successfully, but does NOT call `control_air_circulator()` when you speak.

## 🎯 Root Cause
**VAPI is configured to TALK instead of calling functions for device control.**

## 📋 Fix in VAPI Dashboard

### 1. Model Configuration (MOST IMPORTANT!)

Go to your assistant settings → **Model** section:

Check these settings:

#### a. Tool Choice
Look for a setting called:
- **"Tool Choice"** or
- **"Function Calling"** or
- **"Tools Mode"**

Set it to:
- `"auto"` ← Best option
- OR `"required"` ← Forces function calls
- NOT `"none"` ← This disables functions!

#### b. Model Type
Ensure you're using:
- ✅ GPT-4
- ✅ GPT-4-turbo
- ✅ GPT-4o
- ❌ NOT GPT-3.5 (unreliable with functions)

### 2. System Prompt

Copy EXACTLY from: `/Users/karthi/business/tetradapt/secure_voice/config/FORCE_FUNCTION_PROMPT.txt`

**Critical parts:**
```
You MUST call functions. Never respond with text alone.

EVERY OTHER MESSAGE about fan/device:
ALWAYS call control_air_circulator(device, action) FIRST

MAP USER WORDS TO FUNCTION CALLS:
"turn on" → control_air_circulator(device="power", action="turn_on")
```

### 3. Advanced Settings

Some VAPI versions have:

- **Temperature**: Set to 0 or 0.1 (more deterministic)
- **Max Tokens**: At least 150
- **Top P**: 1.0

### 4. Test in VAPI Playground

VAPI dashboard should have a "Test" or "Playground" feature:

1. Click "Test" or "Playground"
2. Type: "turn on the fan"
3. Look at the **debug panel** or **messages**
4. You should see: `tool_calls` or `function_calls`
5. If you DON'T see function calls → Model settings wrong!

### 5. Check Tool Definitions

In VAPI, click on each tool and verify:

**home_auth tool:**
```json
{
  "type": "function",
  "function": {
    "name": "home_auth",
    "description": "Authenticate user. Call immediately on first turn.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
```
**NO server section!**

**control_air_circulator tool:**
```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Control air circulator fan",
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
**NO server section!**

## 🔍 How to Verify It's Fixed

After making changes:

1. Start client: `python src/vapi_client_clean.py`
2. Say "Luna" → Should say "Ready" ✅
3. Say "Turn on the fan"
4. Check Railway logs for:
   ```
   🔍 WEBHOOK DEBUG - Message type: function-call
   ```
5. If you see `function-call` → Fixed! ✅
6. If you see `user-message` → Still broken ❌

## 🎯 The KEY Setting

**The most common issue**: "Tool Choice" is set to `"none"` or not set at all.

**Look for this setting and change it to `"auto"`!**

Different VAPI versions call it:
- "Tool Choice"
- "Function Calling Mode"
- "Tools"
- "Enable Functions"

Find it and enable it!

---

Without seeing your actual VAPI dashboard, the most likely fix is changing **Tool Choice to "auto"**.
