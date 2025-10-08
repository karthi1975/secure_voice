# Setup Instructions - Secure Voice Assistant

## Overview
This voice assistant uses VAPI's Python SDK to enable **real-time voice interaction** with your smart home devices. VAPI handles:
- ✅ Microphone capture
- ✅ Speech-to-text conversion
- ✅ AI processing
- ✅ Text-to-speech response

## Prerequisites
- Python 3.8+
- VAPI account with API key
- Configured VAPI assistant (see VAPI_SYSTEM_PROMPT.md)

## Step 1: Setup Virtual Environment

```bash
# Navigate to project
cd /Users/karthi/business/tetradapt/secure_voice

# Activate virtual environment
source venv/bin/activate

# Install dependencies (including vapi_python)
pip install -r requirements.txt
```

## Step 2: Configure Credentials

Your `config/config.json` should look like this:

```json
{
  "customer_id": "urbanjungle",
  "password": "alpha-bravo-123",
  "vapi_assistant_id": "31377f1e-dd62-43df-bc3c-ca8e87e08138",
  "vapi_api_key": "9dd4eed1-01a1-4d6f-baae-40b060bc98d4"
}
```

**Important Notes:**
- `customer_id`: Your home/location identifier
- `password`: Password prepended to commands for authentication
- `vapi_assistant_id`: Your VAPI assistant ID from dashboard
- `vapi_api_key`: Your VAPI API key

## Step 3: Run the Voice Assistant

### Option A: Interactive Menu
```bash
python3 src/vapi_voice_client.py
```

Then choose:
- **Option 1**: 30-second voice session (good for testing)
- **Option 2**: Continuous session (runs until Ctrl+C)
- **Option 3**: Custom greeting message

### Option B: Direct Python Usage
```python
from src.vapi_voice_client import SecureVoiceAssistant

# Initialize
assistant = SecureVoiceAssistant("config/config.json")

# Start continuous session
assistant.start_continuous_session()
```

## Step 4: Using the Voice Assistant

Once the session starts:

1. **VAPI activates your microphone** automatically
2. **Speak naturally** - say commands like:
   - "Turn on the fan"
   - "Set living room lights to 75%"
   - "Lock the front door"
   - "What's the temperature?"

3. **Luna responds** with voice confirmation

## How It Works

```
┌─────────────────────────────────────────┐
│ 1. YOU SPEAK                            │
│    "Turn on the fan"                    │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. VAPI SDK (on your computer)          │
│    - Captures microphone audio          │
│    - Sends to VAPI servers              │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. VAPI CLOUD PROCESSING                │
│    - Speech-to-text: "Turn on the fan"  │
│    - Prepend password (by client)       │
│    - LLM processes command              │
│    - Validates password                 │
│    - Calls control_device()             │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 4. VAPI RESPONDS                        │
│    - Text: "Turning on the fan"         │
│    - Converts to speech                 │
│    - Plays audio through speakers       │
└─────────────────────────────────────────┘
```

## Password Flow

The password is automatically prepended by the client:

```python
# User says: "Turn on the fan"
# Client sends: "alpha-bravo-123 Turn on the fan"
# VAPI validates password in system prompt
# VAPI processes: "Turn on the fan"
```

## Testing

### Quick Test (30 seconds)
```bash
cd /Users/karthi/business/tetradapt/secure_voice
source venv/bin/activate
python3 src/vapi_voice_client.py
# Choose option 1
# Say: "Turn on the fan"
```

### Continuous Session
```bash
python3 src/vapi_voice_client.py
# Choose option 2
# Speak multiple commands
# Press Ctrl+C when done
```

## Troubleshooting

### "vapi_python not found"
```bash
pip install vapi_python
```

### "VAPI_API_KEY not found"
Make sure your `config/config.json` has `vapi_api_key` field.

### "No microphone access"
VAPI SDK needs microphone permissions. Check:
- System Settings → Privacy & Security → Microphone
- Allow Python/Terminal access

### "Assistant not responding"
1. Verify assistant_id in config.json
2. Check VAPI dashboard for assistant status
3. Ensure system prompt includes password validation (see VAPI_SYSTEM_PROMPT.md)

### "Authentication failed"
- Password in config.json must match password in VAPI system prompt
- Check for typos or extra spaces

## Next Steps

1. **Add webhook endpoint** to actually control devices
2. **Implement control_device function** in VAPI dashboard
3. **Add more devices** to your smart home
4. **Deploy on Raspberry Pi** for always-on voice control

## Architecture Notes

### Why vapi_python SDK?

The SDK handles all the complexity:
- WebRTC streaming
- Audio encoding/decoding
- Connection management
- Session handling

You just call `vapi.start()` and VAPI does the rest!

### Password Security

- Password is prepended **client-side** before sending to VAPI
- Never exposed in UI or logs
- Validated **server-side** by VAPI system prompt
- Each home has unique password

## Files Reference

- `src/vapi_voice_client.py` - Main voice client with SDK integration
- `src/voice_client.py` - Old text-based client (deprecated)
- `config/config.json` - Credentials and configuration
- `VAPI_SYSTEM_PROMPT.md` - System prompt for VAPI assistant
- `config/vapi_function.json` - Function definition for control_device

## Support

If you encounter issues:
1. Check VAPI dashboard for call logs
2. Verify microphone permissions
3. Test with VAPI web console first
4. Check network connectivity

---

**Ready to run!** Just activate venv and run:
```bash
source venv/bin/activate && python3 src/vapi_voice_client.py
```
