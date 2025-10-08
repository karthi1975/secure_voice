# Debug Webhook Flow

## Test the webhook manually to understand the payload structure

### 1. Test session creation
```bash
curl -X POST https://securevoice-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "urbanjungle", "password": "alpha-bravo-123"}'
```

Expected response:
```json
{"sid": "some-uuid-here", "authenticated": false}
```

### 2. Test home_auth with the sid

Replace `YOUR_SID_HERE` with the sid from step 1:

```bash
curl -X POST "https://securevoice-production.up.railway.app/webhook?sid=YOUR_SID_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "home_auth",
        "parameters": {}
      }
    }
  }'
```

Expected response:
```json
{
  "results": [{
    "type": "function-result",
    "name": "home_auth",
    "result": "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"
  }]
}
```

### 3. Test control_air_circulator with the same sid

```bash
curl -X POST "https://securevoice-production.up.railway.app/webhook?sid=YOUR_SID_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "control_air_circulator",
        "parameters": {
          "device": "power",
          "action": "turn_on"
        }
      }
    }
  }'
```

Expected response:
```json
{
  "results": [{
    "type": "function-result",
    "name": "control_air_circulator",
    "result": "Power turn on"
  }]
}
```

## Common Issues

### Issue 1: "Invalid session ID"
- Make sure you're using the exact sid from step 1
- Sessions are stored in memory and will be lost on server restart

### Issue 2: "Not authenticated" for control
- Make sure you ran step 2 (home_auth) first
- The session needs to be marked as authenticated before control works

### Issue 3: Wrong payload structure
VAPI might send the payload differently. The actual structure might be:
```json
{
  "message": {
    "type": "function-call",
    "functionCall": { ... }
  }
}
```

OR it might be:
```json
{
  "type": "function-call",
  "functionCall": { ... }
}
```

Check Railway logs to see the actual payload VAPI sends.
