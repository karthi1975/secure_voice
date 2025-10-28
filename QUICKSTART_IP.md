# Quick Start - IP Address Only

Deploy webhook using only IP address (no domain needed) in 3 steps.

## Step 1: Create Droplet

1. Go to https://cloud.digitalocean.com/droplets
2. Click "Create Droplet"
3. Choose:
   - **Ubuntu 22.04 LTS**
   - **$12/month** (2GB RAM)
   - Add your **SSH key**
4. Click "Create"
5. **Copy the IP address**

## Step 2: Deploy

### From Windows:
```powershell
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice
.\deploy-ip-only.ps1 -DropletIP YOUR_IP
```

### From Linux/Mac:
```bash
ssh root@YOUR_IP
curl -fsSL https://raw.githubusercontent.com/karthi1975/secure_voice/main/deploy-ip-only.sh -o deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

## Step 3: Configure

```bash
# SSH to droplet
ssh root@YOUR_IP

# Edit config
nano /opt/secure_voice/.env
```

Update this line:
```
VAPI_API_KEY=your_actual_vapi_api_key_here
```

Save: `Ctrl+X`, `Y`, `Enter`

```bash
# Restart
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml restart

# Test
curl http://localhost:8001/health
```

## Done! 🎉

**Your webhook URL:**
```
http://YOUR_DROPLET_IP:8001/webhook?device_id={{device_id}}
```

**Update VAPI:**
1. Go to https://dashboard.vapi.ai/
2. Select your assistant
3. Update Server URL to the webhook URL above

## Test from Windows

```powershell
# Health check
Invoke-RestMethod -Uri "http://YOUR_IP:8001/health"
```

## Manage Service

```bash
# View logs
docker-compose -f docker-compose-http.yml logs -f webhook

# Restart
docker-compose -f docker-compose-http.yml restart

# Stop
docker-compose -f docker-compose-http.yml down

# Start
docker-compose -f docker-compose-http.yml up -d
```

## ⚠️ Security Warning

This uses **HTTP** (not HTTPS) - traffic is NOT encrypted.

✅ OK for testing
❌ NOT for production

For production, get a domain and use HTTPS.

## Need HTTPS Without Domain?

Use Cloudflare Tunnel (free):
- See `DEPLOYMENT_IP_ONLY.md` - Cloudflare Tunnel section

## Troubleshooting

**Can't connect?**
```bash
# Check firewall
ssh root@YOUR_IP "ufw status"

# Allow port 8001
ssh root@YOUR_IP "ufw allow 8001/tcp"
```

**Service not running?**
```bash
ssh root@YOUR_IP
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml logs webhook
```

## Cost

- **Droplet**: $12/month
- **Total**: $12/month

## URLs

Replace `YOUR_IP` with your droplet IP:

- Health: `http://YOUR_IP:8001/health`
- Auth: `http://YOUR_IP:8001/device/auth`
- Webhook: `http://YOUR_IP:8001/webhook?device_id={{device_id}}`

## Full Documentation

- Detailed guide: `DEPLOYMENT_IP_ONLY.md`
- Windows guide: `DEPLOYMENT_WINDOWS.md`
- Full setup: `DEPLOYMENT_DIGITALOCEAN.md`
