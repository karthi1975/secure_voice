# 🎤 Secure Voice - VAPI Voice Assistant for Home Automation

Voice-controlled smart home system using VAPI (Voice API) and Home Assistant.

## 🚀 Quick Start

See **QUICK_START.md** for complete setup instructions.

## 🔧 How It Works

```
User Voice → VAPI → Webhook (Railway) → Home Assistant → Physical Device
```

1. **Session Creation**: Client creates session on webhook server, gets session ID (sid)
2. **VAPI Call**: Client sets `serverUrl` with `?sid=xxx` parameter
3. **Authentication**: VAPI calls `home_auth()` tool, webhook validates credentials
4. **Device Control**: User says command → VAPI calls `control_air_circulator(device, action)`
5. **Webhook Forward**: Webhook forwards to Home Assistant webhook with correct format
6. **Home Assistant**: Automation extracts device/action, controls physical entity

## 📁 Project Structure

```
secure_voice/
├── config/                          # Configuration files
│   ├── config.json                  # Main configuration
│   ├── FUNCTION_CALLING_PROMPT.txt  # VAPI system prompt
│   ├── home_auth_tool.json          # Authentication tool config
│   └── control_air_circulator_tool.json  # Device control tool config
├── src/                             # Source code
│   └── vapi_client_clean.py         # Main VAPI client
├── webhook_service/                 # Railway webhook service
│   ├── main.py                      # FastAPI webhook
│   └── requirements.txt             # Webhook dependencies
├── WORKING_AUTOMATION.yaml          # Home Assistant automation
├── DEPLOYMENT_COMPLETE.md           # Full deployment documentation
├── QUICK_START.md                   # Step-by-step setup guide
└── README.md                        # This file
```

## 💻 Installation

```bash
# Clone repository
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

See **QUICK_START.md** for complete configuration steps:

1. Deploy webhook to Railway
2. Configure VAPI assistant
3. Set up Home Assistant automation
4. Update `config/config.json`

## 🎤 Usage

```bash
source venv/bin/activate
python src/vapi_client_clean.py
```

Say "Luna" to start, then:
- "Turn on the fan"
- "Turn off the fan"
- "Set to medium speed"

## 🎯 Supported Commands

### Power
- "Turn on the fan" / "Turn off the fan"

### Speed
- "Set to low" / "Set to medium" / "Set to high"

### Oscillation
- "Turn on oscillation" / "Turn off oscillation"

### Sound
- "Turn on sound" / "Turn off sound"

## 🔐 Security

- Session-based authentication using unique session IDs
- Credentials stored server-side, not in VAPI
- HTTPS endpoints for all communication
- Home Assistant webhook with trusted proxy configuration

## 📚 Documentation

- **QUICK_START.md** - Complete setup guide with troubleshooting
- **DEPLOYMENT_COMPLETE.md** - Full technical documentation
- **WORKING_AUTOMATION.yaml** - Home Assistant automation template

## 🔍 Troubleshooting

See **QUICK_START.md** for detailed troubleshooting steps.

### Quick Checks

1. **Function calls not working**: Update VAPI system prompt from `config/FUNCTION_CALLING_PROMPT.txt`
2. **Home Assistant not responding**: Update automation from `WORKING_AUTOMATION.yaml`
3. **Authentication fails**: Check `config/config.json` credentials
4. **Webhook errors**: Verify Railway deployment at `/health` endpoint

## 🚢 Deployment

### Railway Webhook
- Auto-deploys from `main` branch
- Root directory: `webhook_service`
- Health check: `https://your-webhook.railway.app/health`

### Home Assistant
- Copy automation from `WORKING_AUTOMATION.yaml`
- Settings → Automations → Create Automation → Edit in YAML

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.
