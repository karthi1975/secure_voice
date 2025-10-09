# Authentication Testing Guide

## ✅ What Works

The **server-side authentication is working perfectly**! I've tested it and confirmed:

```bash
./test_auth_only.sh
```

Result: **✅ AUTHENTICATION SUCCESS!**

## 🔍 The Problem

You're getting "Authentication Failed" when running the actual VAPI client, which means one of these issues:

1. **VAPI is not calling `home_auth()` at all**
2. **VAPI is sending a different message format**
3. **The session ID (sid) is not being passed correctly**

## 📋 Step-by-Step Testing Process

### Step 1: Test Local Authentication (DONE ✅)

```bash
./test_auth_only.sh
```

This confirms the server endpoints work correctly.

### Step 2: Run VAPI Client with Enhanced Logging

```bash
./venv/bin/python src/vapi_client_clean.py
```

Look for these logs:
- ✅ Session created
- 🔑 Session ID
- 🔗 Server URL with sid parameter

### Step 3: Check Railway Logs for VAPI Requests

The webhook has debug logging that shows:
- Full payload from VAPI
- Message type
- Session ID (sid)

To see these logs, you need to check Railway dashboard or use:
```bash
railway logs
```

(Note: You'll need to run `railway link` first to connect to your project)

### Step 4: Verify VAPI Assistant Configuration

The VAPI assistant needs these tools configured:

#### Tool 1: home_auth
```json
{
  "type": "function",
  "function": {
    "name": "home_auth",
    "description": "Authenticate the user. MUST be called FIRST when the call starts, before any other function.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
```

#### Tool 2: control_air_circulator
```json
{
  "type": "function",
  "function": {
    "name": "control_air_circulator",
    "description": "Control the air circulator/fan. Can only be called AFTER home_auth() succeeds.",
    "parameters": {
      "type": "object",
      "properties": {
        "device": {
          "type": "string",
          "enum": ["power", "speed"],
          "description": "Device to control"
        },
        "action": {
          "type": "string",
          "enum": ["turn_on", "turn_off", "low", "medium", "high"],
          "description": "Action to perform"
        }
      },
      "required": ["device", "action"]
    }
  }
}
```

### Step 5: Verify serverUrl Override

When the client starts, it should show:
```
🔗 Server URL: https://securevoice-production.up.railway.app/webhook?sid=<your-sid>
```

This URL should be set as the `serverUrl` in the VAPI assistant override.

## 🐛 Debugging Checklist

- [ ] Session is created successfully (check client logs)
- [ ] SID is included in serverUrl (`/webhook?sid=xxxxx`)
- [ ] VAPI assistant has `home_auth` tool defined
- [ ] Assistant prompt tells Luna to call `home_auth()` FIRST
- [ ] Railway logs show incoming webhook requests
- [ ] Railway logs show the correct sid parameter
- [ ] Railway logs show `home_auth` function being called

## 🔧 Next Steps

1. **Run the client** and copy the Session ID
2. **Check Railway logs** to see if VAPI is making requests
3. **Look for debug output** like:
   ```
   🔍 WEBHOOK DEBUG - Full payload: {...}
   🔍 WEBHOOK DEBUG - SID: xxxxx
   🔍 WEBHOOK DEBUG - Message type: function-call
   ```

4. If you see "Authentication failed" in Luna's response, check:
   - Is the customer_id "urbanjungle"?
   - Is the password "alpha-bravo-123"?
   - Are these stored in the session correctly?

## ✅ Success Criteria

When authentication works, you should hear Luna say:
> "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"

Then you can test fan commands:
- "Turn on the fan"
- "Set to medium speed"
- "Turn off the fan"
