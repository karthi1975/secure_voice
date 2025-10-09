# 🧪 Simple Test Setup - No Authentication

This is a simplified version to test if VAPI function calling works at all.

## ⚠️ Warning
- **NO authentication** - Anyone can control the fan
- **For testing only** - Not secure for production
- Direct VAPI → Home Assistant (no Railway middleware)

## 📋 Setup Steps

### 1. Update VAPI Assistant Configuration

Go to VAPI dashboard → Your assistant (ID: `31377f1e-dd62-43df-bc3c-ca8e87e08138`)

#### a. System Prompt
Copy from: `/Users/karthi/business/tetradapt/secure_voice/config/SIMPLE_PROMPT.txt`

Paste entire content as your assistant's system prompt.

#### b. Tool Configuration
1. **Remove** the `home_auth` tool (not needed for this test)
2. **Replace** `control_air_circulator` tool with content from:
   `/Users/karthi/business/tetradapt/secure_voice/config/SIMPLE_TOOL_FOR_VAPI.json`

**Important**: This tool has `server.url` pointing directly to Home Assistant!

#### c. First Message Mode
Set to: **"Assistant waits for user"**

#### d. Model Settings
- **Model**: GPT-4 or GPT-4o
- **Tool Choice** (if available): Set to "auto" or "required"
- **Temperature**: 0 or 0.1

### 2. Run Simple Client

```bash
python src/vapi_client_simple.py
```

### 3. Test Commands

Say:
- "Turn on the fan" → Fan should turn ON
- "Turn off the fan" → Fan should turn OFF
- "Set to medium" → Fan should change speed

## 🔍 What to Check

### If it WORKS:
✅ VAPI function calling is working!
✅ Home Assistant webhook is receiving calls
✅ Problem was with the dynamic serverUrl approach

**Solution**: Keep direct server URL in tool, or fix VAPI to support dynamic serverUrl

### If it DOESN'T WORK:
❌ VAPI function calling configuration issue
❌ Check: Tool Choice setting
❌ Check: Model (must be GPT-4, not GPT-3.5)
❌ Check: System prompt is actually saved

## 📊 Files Created

1. **Client**: `src/vapi_client_simple.py` - Simple VAPI client (no auth)
2. **Prompt**: `config/SIMPLE_PROMPT.txt` - Minimal system prompt
3. **Tool**: `config/SIMPLE_TOOL_FOR_VAPI.json` - Tool with direct HA URL

## 🔙 Going Back to Secure Version

After testing, if you want to go back to secure authenticated version:

1. Use `src/vapi_client_clean.py` instead
2. Add back `home_auth` tool
3. Remove `server.url` from tools
4. Use longer system prompt with authentication

## 🎯 Expected Result

This simple version should work if:
1. VAPI function calling is enabled (Tool Choice = auto)
2. Home Assistant webhook is working (we know it is!)
3. System prompt is clear about calling functions

If this simple version works, we can add authentication back!

---

**Start here**: Copy `SIMPLE_PROMPT.txt` and `SIMPLE_TOOL_FOR_VAPI.json` to VAPI dashboard, then run `vapi_client_simple.py`!
