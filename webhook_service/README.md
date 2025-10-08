# VAPI Authentication Webhook Service

Webhook service for validating customer credentials in VAPI voice sessions.

## Valid Credentials

- **customer_id**: `urbanjungle`
- **password**: `alpha-bravo-123`

## Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /auth` - Main authentication endpoint
- `POST /webhook` - Generic webhook endpoint

## Deploy to Railway

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Deploy
```bash
cd webhook_service
railway init
railway up
```

### 4. Get your webhook URL
```bash
railway domain
```

You'll get a URL like: `https://your-app.railway.app`

### 5. Configure in VAPI

In VAPI Dashboard:
1. Go to your assistant settings
2. Add Server URL: `https://your-app.railway.app/auth`
3. Set trigger: "On message received"
4. Save

## Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Test authentication
curl -X POST http://localhost:8001/auth \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "user",
      "content": "urbanjungle:alpha-bravo-123 Hello"
    }
  }'
```

## Expected Responses

### Valid Credentials
```json
{
  "results": [{
    "type": "assistant-message",
    "message": "Welcome! Authentication successful. I'm Luna, your smart home assistant for urbanjungle. How can I help you today?"
  }]
}
```

### Invalid Credentials
```json
{
  "results": [{
    "type": "assistant-message",
    "message": "Authentication failed"
  }]
}
```

## Environment Variables

None required! Credentials are hardcoded for security.

## VAPI System Prompt

Use this in your VAPI assistant:

```
You are Luna, a smart home assistant for urbanjungle.

When you receive your first message, it will be forwarded to a webhook for authentication.

The webhook validates credentials and returns a response.

Use the webhook response as your greeting.

After authentication, help users control:
- Fans (on/off, speed)
- Lights (on/off, brightness)
- Locks (lock/unlock)
- Thermostat (temperature)

Be friendly and brief.
```

## Security

- Credentials validated server-side
- No credentials exposed in responses
- CORS enabled for VAPI
- Health check for monitoring

## Monitoring

Check service health:
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```
