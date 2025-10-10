# 🔊 Secure Voice - Multi-Tenant Voice Control for Smart Homes

Production-ready, secure voice assistant system using VAPI AI with multi-tenant support. Perfect for deploying voice control to multiple Raspberry Pi devices across different customer homes.

## ✨ Features

- 🔒 **Fully Secure** - VAPI API key never stored on edge devices
- 🏠 **Multi-Tenant** - Support multiple customers/homes from one server
- ♾️ **Always-On** - Auto-restart on call end, perfect for 24/7 operation
- 🔑 **JWT Authentication** - Short-lived tokens (15 min) for device access
- 🌐 **Webhook Routing** - Automatic routing to correct Home Assistant instance
- 📡 **Centralized Config** - Update VAPI settings without touching Pi devices

## 🏗️ Architecture

```
Raspberry Pi (Edge Device)
    ↓ [Authenticates with device_id + device_secret]
Railway Proxy Server
    ↓ [Returns JWT token + VAPI config]
VAPI Voice AI Platform
    ↓ [Function calls → serverUrl with device_id]
Railway Webhook Handler
    ↓ [Routes by device_id → customer_id]
Home Assistant Instance
    ↓ [Controls physical devices]
Smart Home Devices (Fans, Lights, etc.)
```

See **ARCHITECTURE.md** for detailed flow diagrams.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- VAPI account with API key
- Railway account (free tier works)
- Home Assistant instance

### 1. Deploy Railway Server

```bash
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice
railway up
```

Set environment variables in Railway:
- `VAPI_API_KEY` - Your VAPI public API key
- `VAPI_ASSISTANT_ID` - Your VAPI assistant ID
- `JWT_SECRET` - Random secret for JWT tokens

### 2. Configure Raspberry Pi

```bash
# Install dependencies
pip install vapi-python python-dotenv httpx

# Configure device
cat > config/device_config.json << EOF
{
  "device_id": "pi_customer_001",
  "device_secret": "your-secret-here",
  "proxy_url": "https://your-railway-app.railway.app"
}
EOF

# Run client
python src/vapi_client_sdk.py
```

### 3. Configure VAPI Assistant

In VAPI Dashboard, create an assistant with:
- **Model**: GPT-4 or similar
- **Voice**: Choose your preferred voice
- **System Prompt**: See `VAPI_SYSTEM_PROMPT_AIR_CIRCULATOR.txt`
- **Tools**: Add `control_air_circulator` function (see `config/FRONT_DOOR_TOOL_FOR_VAPI.json`)

### 4. Configure Home Assistant

Add automation from `HA_AUTOMATION_SIMPLE.yaml`:
- Create webhook trigger with ID `vapi_air_circulator`
- Add conditions for device/action matching
- Add actions to control devices

## 📁 Project Structure

```
secure_voice/
├── src/
│   └── vapi_client_sdk.py          # Production client (Pi)
├── config/
│   ├── device_config.json           # Device credentials
│   ├── FRONT_DOOR_TOOL_FOR_VAPI.json # Example tool config
│   └── VAPI_SYSTEM_PROMPT_AIR_CIRCULATOR.txt # Example prompt
├── webhook_service/                 # Railway server
│   ├── main.py                      # Main webhook handler
│   ├── device_auth.py               # JWT authentication
│   ├── ha_instances.py              # Multi-tenant routing
│   └── requirements.txt             # Server dependencies
├── HA_AUTOMATION_SIMPLE.yaml        # Home Assistant automation
├── ARCHITECTURE.md                  # Architecture flow diagrams
├── README.md                        # This file
└── requirements.txt                 # Client dependencies
```

## 🎤 Usage

### Start the Voice Client

```bash
python src/vapi_client_sdk.py
```

The client will:
1. Authenticate with Railway server
2. Fetch VAPI configuration
3. Start voice call with webhook routing
4. Auto-restart if call ends
5. Run forever until manually stopped (Ctrl+C)

### Voice Commands

Say commands like:
- "Turn on the fan"
- "Set fan to medium speed"
- "Turn off the fan"

## 🔐 Security Architecture

### Tier 0 Security - Zero Secrets on Edge Devices

**What's stored on Pi:**
- ✅ Device ID (not secret)
- ✅ Device secret (like a password for this specific Pi)
- ✅ Proxy URL (public)

**What's NEVER on Pi:**
- ❌ VAPI API key
- ❌ Home Assistant credentials
- ❌ Customer data

**How it works:**
1. Pi authenticates → gets short-lived JWT (15 min)
2. Pi requests VAPI config → server provides it
3. JWT expires → Pi auto-refreshes
4. Compromised Pi → revoke device_secret, no API keys exposed

## 🏠 Multi-Tenant Support

### Adding New Customer

1. **Add device to Railway** (`webhook_service/device_auth.py`):
```python
DEVICES = {
    "pi_newcustomer_001": {
        "device_secret": "dev_secret_newcustomer_xyz789",
        "customer_id": "newcustomer",
        # ...
    }
}
```

2. **Add HA instance** (`webhook_service/ha_instances.py`):
```python
HA_INSTANCES = {
    "newcustomer": {
        "ha_url": "https://newcustomer-ha.example.com",
        "ha_webhook_id": "vapi_voice",
        "name": "New Customer Home"
    }
}
```

3. **Deploy Pi** with new `device_id` and `device_secret`

That's it! Automatic routing to correct HA instance.

## 🔧 API Endpoints

### Railway Server

- `POST /device/auth` - Authenticate device, get JWT
- `POST /device/refresh` - Refresh JWT token
- `GET /device/vapi-config` - Get VAPI config (API key + assistant ID)
- `POST /webhook` - VAPI webhook handler (multi-tenant routing)
- `GET /health` - Health check

### Authentication Flow

```bash
# 1. Authenticate
curl -X POST https://your-railway-app.railway.app/device/auth \
  -H "Content-Type: application/json" \
  -d '{"device_id": "pi_customer_001", "device_secret": "secret"}'

# Returns: {"access_token": "eyJ...", "expires_in": 900}

# 2. Get VAPI config
curl https://your-railway-app.railway.app/device/vapi-config \
  -H "Authorization: Bearer eyJ..."

# Returns: {"api_key": "...", "assistant_id": "..."}
```

## 📊 Monitoring

### Railway Logs

```bash
railway logs
```

Look for:
- `✅ Device authenticated: pi_xxx → customer: yyy`
- `✅ Routed via device_id: pi_xxx → customer: yyy → HA: zzz`
- `🏠 Using HA for customer: https://...`

### Health Check

```bash
curl https://your-railway-app.railway.app/health
```

## 🐛 Troubleshooting

### Client won't start
- Check `config/device_config.json` exists
- Verify `device_id` and `device_secret` are correct
- Test Railway server: `curl https://your-app.railway.app/health`

### Authentication fails
- Check device credentials in `webhook_service/device_auth.py`
- Verify JWT_SECRET is set in Railway
- Check Railway logs for error messages

### Voice call doesn't start
- Verify VAPI_API_KEY is set in Railway
- Check VAPI assistant ID is correct
- Test VAPI dashboard to ensure assistant exists

### Function calls not working
- Check webhook URL includes `device_id` parameter
- Verify HA webhook ID matches automation trigger
- Check HA automation is enabled
- Review Railway logs for routing info

## 🚢 Production Deployment

### Systemd Service (Pi)

Create `/etc/systemd/system/voice-client.service`:

```ini
[Unit]
Description=Secure Voice Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/secure_voice
ExecStart=/home/pi/secure_voice/venv/bin/python src/vapi_client_sdk.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable voice-client
sudo systemctl start voice-client
sudo systemctl status voice-client
```

### Railway Production

- Railway auto-deploys from `main` branch
- Set production environment variables
- Monitor with `railway logs`
- Health check: `https://your-app.railway.app/health`

## 📝 License

MIT

## 🙏 Credits

Built with:
- [VAPI](https://vapi.ai) - Voice AI platform
- [Railway](https://railway.app) - Deployment platform
- [Home Assistant](https://www.home-assistant.io) - Smart home platform

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/karthi1975/secure_voice/issues
- Documentation: See ARCHITECTURE.md for detailed flow diagrams
