# Session-Based Authentication Setup

This implementation uses **session IDs (sid)** to securely authenticate VAPI voice sessions.

## How It Works

### Flow:

```
1. Client → Server: POST /sessions with credentials
2. Server → Client: Returns sid (session ID)
3. Client → VAPI: Start call with tools that have ?sid=xxx in URLs
4. VAPI → Server: POST /auth?sid=xxx (home_auth tool call)
5. Server: Validates session, marks authenticated
6. User: "Hey Luna, turn on the fan"
7. VAPI → Server: POST /control?sid=xxx (control_air_circulator tool call)
8. Server: Checks if session is authenticated, then controls device
```

### Key Points:

- **No credentials in voice**: Credentials never spoken or sent in conversation
- **Session-based**: Each call gets a unique sid
- **Stateful auth**: Server tracks which sessions are authenticated
- **Tool URL override**: Client overrides tool URLs with `?sid=xxx` parameter

## Deployment Steps

### 1. Deploy Webhook to Railway

```bash
cd webhook_service

# Deploy
railway up

# Verify deployment
curl https://healthy-alley-production.up.railway.app/health
# Should return: {"status":"healthy"}
```

### 2. Test Session Creation

```bash
curl -X POST https://healthy-alley-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"urbanjungle","password":"alpha-bravo-123"}'

# Should return: {"sid":"<uuid>","authenticated":false}
```

### 3. Run the Client

```bash
# Activate virtual environment
source venv/bin/activate

# Run client
python src/vapi_client_clean.py
```

### Expected Output:

```
============================================================
🎤 VAPI Voice Assistant - Session Authentication
============================================================
👤 Customer: urbanjungle
🔐 Password: ***************
🌐 API Base: https://healthy-alley-production.up.railway.app
============================================================

🔑 Creating session...
✅ Session created: a1b2c3d4...

📞 Starting VAPI call with sid-based tools...
✅ Voice session started!
📱 Call ID: xxx
🔑 Session ID: a1b2c3d4...

============================================================
🔊 Luna will authenticate automatically
============================================================

🗣️  Start speaking after you hear Luna's greeting...

💡 Example commands:
   - 'Hey Luna, turn on the fan'
   - 'Luna, set to medium'
   - 'Turn on oscillation'

🔴 Session is LIVE. Press Ctrl+C to stop.
```

## What Happens When You Speak

### 1. First Interaction (Automatic):

**Luna says:** "Hi! Authenticating..."
- Assistant automatically calls `home_auth()`
- VAPI hits: `https://healthy-alley-production.up.railway.app/auth?sid=<your-sid>`
- Server validates session credentials
- If valid: marks session as authenticated
- **Luna says:** "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"

### 2. Device Commands:

**You say:** "Hey Luna, turn on the fan"
- Assistant calls `control_air_circulator(device="power", action="turn_on")`
- VAPI hits: `https://healthy-alley-production.up.railway.app/control?sid=<your-sid>`
- Server checks if session is authenticated
- If authenticated: processes command
- **Luna says:** "Fan on"

## API Endpoints

### POST /sessions
Create a new session.

**Request:**
```json
{
  "customer_id": "urbanjungle",
  "password": "alpha-bravo-123"
}
```

**Response:**
```json
{
  "sid": "a1b2c3d4-...",
  "authenticated": false
}
```

### POST /auth?sid=xxx
Authenticate a session (called by home_auth tool).

**Response:**
```json
{
  "result": "{\"success\": true, \"message\": \"Welcome! Authentication successful...\"}"
}
```

### POST /control?sid=xxx
Control device (called by control_air_circulator tool).

**Request Body (from VAPI):**
```json
{
  "message": {
    "functionCall": {
      "name": "control_air_circulator",
      "parameters": {
        "device": "power",
        "action": "turn_on"
      }
    }
  }
}
```

**Response:**
```json
{
  "result": "{\"success\": true, \"message\": \"Power turn on\"}"
}
```

## Troubleshooting

### Session not created
- Check Railway logs: `railway logs`
- Verify webhook is deployed: `curl https://healthy-alley-production.up.railway.app/health`

### Authentication failed
- Check credentials in `config/config.json`
- Verify session was created (check client output for sid)
- Check Railway logs for /auth requests

### Device control not working
- Ensure authentication succeeded first
- Check Railway logs for /control requests
- Verify session is marked as authenticated

## Files Modified

### Server (webhook_service/main.py):
- Added session store
- Added `POST /sessions` endpoint
- Updated `POST /auth` to use sid parameter
- Added `POST /control` endpoint with auth check

### Client (src/vapi_client_clean.py):
- Added `_create_session()` method
- Updated `start_session()` to override tool URLs with sid
- Added inline tool definitions with sid parameter

## Security Notes

- Sessions stored in-memory (use Redis in production)
- No session expiration (add TTL in production)
- No rate limiting (add in production)
- Credentials validated server-side only
- sid is a UUID4 (cryptographically random)
