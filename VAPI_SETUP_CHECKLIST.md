# 🔧 VAPI Dashboard Setup Checklist

## Problem: Luna just repeats what you say instead of calling functions

This happens when tools are not properly attached to the assistant.

## ✅ Step-by-Step Fix

### 1. Go to VAPI Dashboard
https://dashboard.vapi.ai

### 2. Find Your Assistant
- Assistant ID: `31377f1e-dd62-43df-bc3c-ca8e87e08138`
- Name: Luna (or whatever you named it)

### 3. Check Tools Section

Click on your assistant → Look for **"Tools"** or **"Functions"** section

You MUST have these 2 tools attached:

#### Tool 1: home_auth
```json
{
  "type": "function",
  "function": {
    "name": "home_auth",
    "description": "Authenticate the user at the start of the conversation. Call this IMMEDIATELY on first turn.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
```

**CRITICAL**: This tool should have **NO** `server` or `server.url` field!

#### Tool 2: control_air_circulator
```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Control the air circulator fan (power, speed, oscillation, sound)",
    "parameters": {
      "type": "object",
      "properties": {
        "device": {
          "type": "string",
          "enum": ["power", "speed", "oscillation", "sound"],
          "description": "Which aspect to control"
        },
        "action": {
          "type": "string",
          "description": "Action to perform: turn_on, turn_off, low, medium, high"
        }
      },
      "required": ["device", "action"]
    }
  }
}
```

**CRITICAL**: This tool should also have **NO** `server` or `server.url` field!

### 4. Remove Any Individual server.url

If you see ANY of these tools have a `server` section like:
```json
{
  "server": {
    "url": "https://..."
  }
}
```

**DELETE IT!** The individual tool URLs override the client's `serverUrl`.

### 5. System Prompt

Make sure your system prompt explicitly tells Luna to call functions:

Copy from: `/Users/karthi/business/tetradapt/secure_voice/config/VAPI_SYSTEM_PROMPT_NO_GREETING.txt`

Key parts:
```
## CRITICAL RULES
1. FIRST turn ONLY: Call home_auth() function immediately
2. ALL other turns: For device commands, call control_air_circulator() function first
```

### 6. First Message Mode

Set to: **"Assistant waits for user"** (you already have this ✅)

### 7. Test

After making these changes:

```bash
python src/vapi_client_clean.py
```

You should see in the terminal:
```
Function call: home_auth
Result: Authentication successful
```

Then say "Turn on the fan" and you should see:
```
Function call: control_air_circulator
Parameters: {"device": "power", "action": "turn_on"}
```

## 🔍 How to Check if Tools Are Attached

In VAPI dashboard:
1. Click your assistant
2. Look for **"Tools"**, **"Functions"**, or **"Server Messages"** tab
3. You should see **2 functions listed**:
   - home_auth
   - control_air_circulator

If you DON'T see these, click "Add Tool" or "Add Function" and add them!

## 📋 Quick Reference Files

- Tool definitions: `config/home_auth_tool.json` and `config/control_air_circulator_tool.json`
- System prompt: `config/VAPI_SYSTEM_PROMPT_NO_GREETING.txt`

## 🚨 Most Common Issues

1. **Tools not attached** → Add them in VAPI dashboard
2. **Individual server.url set** → Remove it from each tool
3. **System prompt not updated** → Copy new prompt
4. **Wrong first message mode** → Set to "Assistant waits for user"

---

Once you complete this checklist, Luna will actually CALL the functions instead of just repeating what you say!
