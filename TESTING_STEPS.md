# Testing if Luna Calls home_auth()

## 🎯 Goal
Verify if Luna (VAPI) is actually calling the `home_auth()` function when the session starts.

## 📋 Step-by-Step Test Process

### Step 1: Prepare Two Terminal Windows

**Terminal 1**: VAPI Client
**Terminal 2**: Railway Logs

---

### Step 2: Start Railway Logs (Terminal 2)

```bash
# Option A: Interactive link
railway link
# Select: jubilant-motivation
# Then:
railway logs --follow

# Option B: Direct web dashboard
# Go to: https://railway.app/dashboard
# Find project: jubilant-motivation
# Click on service → View Logs
```

---

### Step 3: Run VAPI Client (Terminal 1)

```bash
./venv/bin/python src/vapi_client_clean.py
```

**Look for this output:**
```
✅ Session created: 1a2b3c4d...
🔑 Full Session ID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p
🔗 Server URL: https://securevoice-production.up.railway.app/webhook?sid=1a2b3c4d...
```

**Copy the Session ID!**

---

### Step 4: Watch Railway Logs (Terminal 2)

Within **2-3 seconds** of the VAPI client starting, you should see in Railway logs:

#### ✅ If Luna IS Calling home_auth():
```
🔍 WEBHOOK DEBUG - Full payload: {
  "message": {
    "type": "function-call",
    "functionCall": {
      "name": "home_auth",
      "parameters": {}
    }
  },
  "call": {...}
}
🔍 WEBHOOK DEBUG - SID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p
🔍 WEBHOOK DEBUG - Message type: function-call
```

#### ❌ If Luna IS NOT Calling home_auth():
- **No logs appear at all** = VAPI is not calling your webhook
- This means:
  - serverUrl override isn't working
  - OR VAPI assistant configuration is wrong

---

### Step 5: Interpret Results

#### Case A: You See Logs ✅
Luna IS calling the webhook! Now check:

1. **Is the function name `home_auth`?**
   - YES → Good! Check the response
   - NO → Luna is calling a different function

2. **Does the response say "Authentication failed"?**
   - Look for what credentials were used
   - Check if customer_id = "urbanjungle"
   - Check if password = "alpha-bravo-123"

#### Case B: You See NO Logs ❌
Luna is NOT calling the webhook at all!

**Possible causes:**
1. **serverUrl override not applied** - Check VAPI dashboard
2. **Assistant not configured with home_auth tool**
3. **Assistant prompt doesn't tell Luna to call it immediately**

---

## 🔧 Alternative: Manual Log Check

If you can't get railway CLI working, use the web dashboard:

1. Go to https://railway.app/dashboard
2. Find project "jubilant-motivation"
3. Click on your service
4. Click "Logs" tab
5. Keep this open while running the VAPI client
6. Watch for the debug messages

---

## 📊 What You Should Hear

**If authentication works:**
```
[VAPI connects]
[1-2 seconds of silence while Luna calls home_auth()]
Luna: "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"
```

**If authentication fails:**
```
[VAPI connects]
[1-2 seconds of silence]
Luna: "Authentication failed, please try again"
```

**If Luna doesn't call home_auth() at all:**
```
[VAPI connects]
Luna: [Waits for you to speak, or says something generic]
```

---

## 🚀 Quick Test Commands

```bash
# Terminal 1: Start client
./venv/bin/python src/vapi_client_clean.py

# Terminal 2: Watch logs
railway logs --follow

# Alternative: Use web dashboard
open https://railway.app/dashboard
```

---

## 🐛 Debugging Checklist

- [ ] VAPI client starts successfully
- [ ] Session ID is created
- [ ] serverUrl includes `?sid=xxx`
- [ ] Railway logs show incoming requests
- [ ] Request contains `"name": "home_auth"`
- [ ] Response contains success message
- [ ] Luna speaks the success message

---

## 📝 Notes

The webhook has debug logging that prints:
- Full payload from VAPI
- Session ID (sid)
- Message type
- Function name

If you see these logs, it means VAPI is calling your webhook correctly!
