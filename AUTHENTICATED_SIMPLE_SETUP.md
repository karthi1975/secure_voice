# 🔐 Authenticated Simple Setup - Railway Passthrough

This setup uses Railway as a proxy to forward requests to Home Assistant, keeping the same simple parameters from SIMPLE_TEST_SETUP.md but routing through your Railway server.

## ⚠️ Warning
- **NO authentication** - Anyone can control the fan
- **For testing only** - Not secure for production
- VAPI → Railway → Home Assistant

## 📋 Setup Steps

### 1. Deploy to Railway (if not already deployed)

The webhook service in `webhook_service/main.py` now supports both:
- **Authenticated mode**: With `?sid=xxx` parameter (requires home_auth)
- **Passthrough mode**: Without sid parameter (direct forwarding)

Make sure Railway is deployed and running:
```bash
# Check Railway status
railway status

# Or deploy if needed
railway up
```

Your Railway URL should be: `https://securevoice-production.up.railway.app`

### 2. Update VAPI Assistant Configuration

Go to VAPI dashboard → Your assistant (ID: `31377f1e-dd62-43df-bc3c-ca8e87e08138`)

#### a. System Prompt
Copy from: `/Users/karthi/business/tetradapt/secure_voice/config/SIMPLE_PROMPT.txt`

Paste entire content as your assistant's system prompt.

#### b. Tool Configuration
1. **Remove** the `home_auth` tool (not needed for this test)
2. **Replace** `control_air_circulator` tool with content from:
   `/Users/karthi/business/tetradapt/secure_voice/config/AUTHENTICATED_TOOL_FOR_VAPI.json`

**Key differences from SIMPLE_TOOL**:
- Server URL points to Railway: `https://securevoice-production.up.railway.app/webhook`
- Railway then forwards to Home Assistant: `https://ut-demo-urbanjungle.homeadapt.us/api/webhook/vapi_air_circulator`
- Same parameters as simple version (device, action)

#### c. First Message Mode
Set to: **"Assistant waits for user"**

#### d. Model Settings
- **Model**: GPT-4 or GPT-4o
- **Tool Choice** (if available): Set to "auto" or "required"
- **Temperature**: 0 or 0.1

### 3. Run Simple Client

```bash
python src/vapi_client_simple.py
```

### 4. Test Commands

Say:
- "Turn on the fan" → Fan should turn ON
- "Turn off the fan" → Fan should turn OFF
- "Set to medium" → Fan should change speed

## 🔍 What to Check

### If it WORKS:
✅ VAPI function calling is working!
✅ Railway passthrough is working!
✅ Home Assistant webhook is receiving calls via Railway

### If it DOESN'T WORK:
❌ Check Railway logs: `railway logs`
❌ Check: Tool Choice setting
❌ Check: Model (must be GPT-4, not GPT-3.5)
❌ Check: System prompt is actually saved

## 🔧 How it Works

```
VAPI
  ↓ (calls control_air_circulator with device/action)
Railway /webhook endpoint (no sid parameter)
  ↓ (extracts parameters, transforms payload)
Home Assistant /api/webhook/vapi_air_circulator
  ↓ (processes fan control)
Fan responds
```

## 📊 Files Created

1. **Tool Config**: `config/AUTHENTICATED_TOOL_FOR_VAPI.json` - Tool pointing to Railway
2. **Server Update**: `webhook_service/main.py` - Updated to support passthrough mode
3. **Client**: `src/vapi_client_simple.py` - Simple VAPI client (no auth)
4. **Prompt**: `config/SIMPLE_PROMPT.txt` - Minimal system prompt

## 🔒 Going to Full Authentication

After testing, to add authentication:

1. Update tool to use `serverUrl` override with `?sid={sid}` (VAPI feature)
2. Add back `home_auth` tool
3. Use `src/vapi_client_authenticated.py` instead
4. Update system prompt to include authentication flow from `config/AUTHENTICATED_SIMPLE_PROMPT.txt`

## 🎯 Expected Result

This version should work because:
1. Railway acts as a simple proxy/forwarder
2. No authentication complexity in VAPI
3. Transforms VAPI payload to Home Assistant format

If this works, we know:
- ✅ Function calling works
- ✅ Railway deployment works
- ✅ Payload transformation works
- ✅ Ready to add authentication layer!

---

**Start here**: Copy `AUTHENTICATED_TOOL_FOR_VAPI.json` to VAPI dashboard, then run `vapi_client_simple.py`!
