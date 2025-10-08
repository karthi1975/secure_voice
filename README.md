# Secure Voice - Smart Home Voice Control System

Password-authenticated voice control for smart home devices via VAPI.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SPEAKS at urbanjungle home                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
User: "Turn on the fan"
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. LOCAL DEVICE (Raspberry Pi)                              │
└─────────────────────────────────────────────────────────────┘

A. Microphone captures audio
B. Load stored config:
   {
     "customer_id": "urbanjungle",
     "password": "alpha-bravo-123",
     "vapi_assistant_id": "31377f1e-dd62-43df-bc3c-ca8e87e08138"
   }

C. Prepend password to user speech (invisible):
   full_text = "alpha-bravo-123 Turn on the fan"

D. Send text to VAPI:
   POST https://api.vapi.ai/v1/conversation
   Body: {
     "assistant_id": "31377f1e-dd62-43df-bc3c-ca8e87e08138",
     "text": "alpha-bravo-123 Turn on the fan"
   }
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. VAPI PROCESSING                                           │
└─────────────────────────────────────────────────────────────┘

A. Password Validation:
   Message: "alpha-bravo-123 Turn on the fan" ✓
   Password matches: TRUE

B. Intent Recognition (LLM):
   Input: "Turn on the fan"
   Parsed:
   - device_type: "fan"
   - device_id: "air_circulator"
   - action: "turn_on"

C. Tool Call:
   VAPI calls: control_device(
     device_type="fan",
     device_id="air_circulator",
     action="turn_on"
   )

D. Response:
   "Turning on the air circulator"
```

## Project Structure

```
secure_voice/
├── src/
│   └── voice_client.py          # Main client implementation
├── config/
│   └── config.json              # Configuration (customer_id, password, assistant_id)
├── VAPI_SYSTEM_PROMPT.md        # System prompt and function definition for VAPI
└── README.md                     # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure VAPI Assistant

1. Go to VAPI dashboard
2. Create a new assistant named "Luna"
3. Copy the system prompt from `VAPI_SYSTEM_PROMPT.md`
4. Add the `control_device` function definition
5. Copy the assistant ID

### 3. Configure Local Client

Edit `config/config.json`:

```json
{
  "customer_id": "urbanjungle",
  "password": "alpha-bravo-123",
  "vapi_assistant_id": "YOUR_ASSISTANT_ID_HERE",
  "vapi_api_key": "YOUR_API_KEY_HERE"
}
```

Or set environment variable:
```bash
export VAPI_API_KEY="your_api_key_here"
```

## Usage

### Interactive Mode (Testing)

```bash
cd /Users/karthi/business/tetradapt/secure_voice
python3 src/voice_client.py
```

Example session:
```
🎤 Secure Voice Client - urbanjungle
Commands: 'quit' to exit
--------------------------------------------------

You: Turn on the fan
⏳ Processing...
✅ Response: {"message": "Turning on the air circulator"}

You: Set living room lights to 75%
⏳ Processing...
✅ Response: {"message": "Setting living room lights to 75% brightness"}

You: quit
Goodbye!
```

### Programmatic Usage

```python
from src.voice_client import SecureVoiceClient

# Initialize client
client = SecureVoiceClient("config/config.json")

# Send command
response = client.send_command("Turn on the fan")
print(response)
```

## Security

- **Password prepending**: Password is added by the client before sending to VAPI
- **Server-side validation**: VAPI system prompt validates password before processing
- **No password exposure**: Password never shown in UI or logs
- **Customer isolation**: Each home has unique customer_id and password

## Supported Commands

### Fans
- "Turn on the fan" (defaults to air_circulator)
- "Turn off the bedroom fan"
- "Turn on the kitchen fan"

### Lights
- "Turn on living room lights"
- "Turn off bedroom lights"
- "Set kitchen lights to 50%"

### Thermostat
- "Set temperature to 72 degrees"
- "Increase temperature"
- "Decrease temperature"

### Locks
- "Lock the front door"
- "Unlock the back door"

## Devices

**Fans:**
- air_circulator (default)
- bedroom_fan
- kitchen_fan

**Lights:**
- living_room
- bedroom
- kitchen

**Thermostat:**
- main_hvac

**Locks:**
- front_door
- back_door

## Error Handling

### Invalid Password
```
Input: "Turn on the fan" (no password)
Response: "Authentication failed. Access denied."
```

### Unknown Device
```
Input: "Turn on the garage fan"
Response: "I don't recognize that device."
```

### Network Error
```python
{
  "error": "Connection timeout",
  "status": "failed"
}
```

## Next Steps

1. **Implement Webhook**: Create endpoint to actually control devices
2. **Add Audio Input**: Integrate speech-to-text for real voice input
3. **Add More Devices**: Expand device catalog
4. **Add Device State**: Track and report device status
5. **Add Scheduling**: Support time-based automation

## Testing

```bash
# Test with mock commands
python3 src/voice_client.py

# Try these commands:
# - Turn on the fan
# - Set living room lights to 50%
# - Lock the front door
# - What's the weather? (should fail gracefully)
```

## Troubleshooting

**"Config file not found"**
- Ensure `config/config.json` exists
- Check path is correct relative to execution directory

**"VAPI_API_KEY not found"**
- Set environment variable: `export VAPI_API_KEY="your_key"`
- Or add `vapi_api_key` to config.json

**"Authentication failed" every time**
- Verify password in config matches VAPI system prompt
- Check password formatting (exact string match required)

**Network timeout**
- Check internet connection
- Verify VAPI API is accessible
- Increase timeout in `send_command` method

## License

MIT
