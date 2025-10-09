# 🧪 Testing Checklist - Voice Control

## What We Just Fixed

1. **Webhook**: Added debug logging to see what VAPI sends
2. **Client**: Removed `firstMessage` so Luna waits for you to speak first

## Railway Deployment Status

Wait for Railway to deploy both changes (~1-2 minutes):
- Webhook service (with debug logging)
- Updated from latest git push

Check deployment: https://railway.app (or check health endpoint)

## Testing Steps

### Step 1: Start Client
```bash
python src/vapi_client_clean.py
```

Expected output:
```
============================================================
🎤 VAPI Voice Assistant - Session Authentication
============================================================
👤 Customer: urbanjungle
🔐 Password: ****************
🌐 API Base: https://securevoice-production-eb77.up.railway.app
============================================================

🔑 Creating session...
✅ Session created: xxxxxxxx...

📞 Starting VAPI call with sid-based serverUrl...
✅ Voice session started!
📱 Call ID: ...
🔑 Session ID: xxxxxxxx...

🔊 Luna will authenticate automatically
...
```

### Step 2: Say "Luna"

You should hear: **SILENCE** (Luna waits for you, no greeting)

### Step 3: Check Railway Logs

Look for:
```
🔍 WEBHOOK DEBUG - Full payload: {...}
🔍 WEBHOOK DEBUG - SID: xxxxxxxx
🔍 WEBHOOK DEBUG - Message type: function-call   <-- GOOD!
```

or

```
🔍 WEBHOOK DEBUG - Message type: user-message    <-- BAD!
```

### Step 4: What Should Happen

**If functions are working:**
1. You say "Luna"
2. Webhook receives: `type: "function-call"`, `name: "home_auth"`
3. Luna says: "Ready" or "Authentication successful"
4. You say: "Turn on the fan"
5. Webhook receives: `type: "function-call"`, `name: "control_air_circulator"`
6. Fan turns ON ✅

**If functions are NOT working:**
1. You say "Luna"
2. Webhook receives: `type: "user-message"` or `type: "assistant-message"`
3. Luna just repeats or says random stuff
4. Functions never called ❌

## Debug Info to Collect

If it still doesn't work, get this info from Railway logs:

1. The FULL JSON payload (from debug log)
2. The message type
3. Whether you see "function-call" anywhere

Paste that here and we'll diagnose!

## VAPI Dashboard Settings to Double-Check

While waiting for deployment:

1. **First Message Mode**: "Assistant waits for user" ✅
2. **Tools**: Both `home_auth` and `control_air_circulator` attached ✅
3. **Tool Server URLs**: REMOVED (no individual server.url) ✅
4. **System Prompt**: Copy from `config/ULTRA_MINIMAL_PROMPT.txt`
5. **Model**: GPT-4 or GPT-4o (not GPT-3.5)
6. **Tool Choice** (if available): Set to "auto" or "required"

---

After Railway deploys (~2 min), run the test!
