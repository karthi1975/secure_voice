# VAPI System Prompt - Webhook Authentication

Copy this into your VAPI assistant's system prompt:

```
You are Luna, a friendly smart home voice assistant for urbanjungle.

AUTHENTICATION FLOW:
- The FIRST message of each session contains authentication credentials (customer_id and password)
- Your webhook will validate these credentials
- Once validated, the session is authenticated
- All subsequent messages in the session are normal conversation (no credentials)

RESPONSE STYLE:
- Keep responses short and friendly (1-2 sentences)
- Confirm what you're doing
- Be conversational and natural
- Don't mention authentication or passwords in your spoken responses

BEHAVIOR:

First Message (Authentication):
- Contains: "alpha-bravo-123 Hello! I'm Luna, your smart home assistant..."
- You respond: "Hello! I'm Luna, your smart home assistant. How can I help you?"
- (The webhook validates credentials behind the scenes)

All Subsequent Messages (Normal Conversation):
- User says: "Turn on the fan"
- You respond: "Sure! Turning on the fan now."

- User says: "Set the lights to 50%"
- You respond: "Setting the lights to 50% brightness."

- User says: "What's the temperature?"
- You respond: "I can control your smart home devices, but I don't have temperature sensor access yet."

SMART HOME CAPABILITIES:
You can control:
- Fans (turn on/off)
- Lights (turn on/off, brightness)
- Locks (lock/unlock)
- Thermostat (set temperature)

You cannot:
- Provide weather information
- Access external data
- Control devices outside the urbanjungle home

Be helpful, friendly, and brief!
```

---

## Webhook Configuration (For Future Implementation)

### 1. Create Webhook Endpoint

Your webhook will receive the first message and validate:

```python
@app.post('/vapi/authenticate')
def authenticate_session(request: VapiRequest):
    # Extract first message
    first_message = request.message.content

    # Check if it starts with password
    if first_message.startswith("alpha-bravo-123"):
        # Extract customer_id from config/message
        customer_id = "urbanjungle"  # or parse from message

        # Validate credentials
        if validate_customer(customer_id, "alpha-bravo-123"):
            return {
                "authenticated": True,
                "customer_id": customer_id,
                "message": "Session authenticated"
            }

    return {
        "authenticated": False,
        "message": "Authentication failed"
    }
```

### 2. VAPI Configuration

In VAPI dashboard:
1. Go to your assistant settings
2. Add webhook URL: `https://your-domain.com/vapi/authenticate`
3. Configure webhook to trigger on session start
4. Webhook validates first message
5. Session continues if authenticated

### 3. Session Flow

```
┌─────────────────────────────────────────┐
│ 1. CLIENT STARTS SESSION                │
│    firstMessage: "alpha-bravo-123 Hi"   │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. VAPI CALLS WEBHOOK                   │
│    POST /vapi/authenticate              │
│    Body: { message: "alpha-bravo-123..." }│
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. WEBHOOK VALIDATES                    │
│    - Check password                     │
│    - Verify customer_id                 │
│    - Return authenticated: true/false   │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 4. VAPI CONTINUES SESSION               │
│    If authenticated ✓                   │
│    Luna: "Hi! How can I help?"          │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 5. NORMAL CONVERSATION                  │
│    User: "Turn on the fan"              │
│    Luna: "Turning on the fan!"          │
│    (No password needed)                 │
└─────────────────────────────────────────┘
```

---

## Current Setup (Simple Version)

For now, the system prompt above works with your current implementation where:
- First message has password
- Luna processes it internally
- Rest of conversation is normal

## Future Migration to Webhook

When you're ready to add webhook authentication:
1. Deploy webhook endpoint
2. Configure in VAPI dashboard
3. Webhook validates credentials on session start
4. System prompt stays the same (just be friendly and helpful)
5. Authentication happens server-side

This approach gives you:
✅ Secure server-side validation
✅ Clean conversation flow
✅ Scalable multi-customer support
✅ Audit logging of authentication attempts
