# Deploy with IP Address Only (No Domain)

Quick guide to deploy the webhook using only the droplet IP address without a domain name.

## Quick Deployment Steps

### 1. Create Digital Ocean Droplet

Create droplet and note the IP address.

### 2. Deploy to Droplet

**From Windows (PowerShell):**
```powershell
.\deploy-to-do.ps1 -DropletIP YOUR_DROPLET_IP
```

**From Linux/Mac/WSL:**
```bash
./deploy-to-do.sh
```

### 3. SSH to Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### 4. Install Docker & Docker Compose

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### 5. Clone Repository

```bash
mkdir -p /opt/secure_voice
cd /opt/secure_voice
git clone https://github.com/karthi1975/secure_voice.git .
```

### 6. Create Environment File

```bash
cat > .env << 'EOF'
# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138

# JWT Secret - CHANGE THIS!
JWT_SECRET=change_this_to_a_random_secret_at_least_32_characters

# Home Assistant Configuration
HOMEASSISTANT_URL=https://ut-demo-urbanjungle.homeadapt.us
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator

# Port
PORT=8001
EOF
```

Edit with your actual values:
```bash
nano .env
```

Update:
- `VAPI_API_KEY` - Your actual VAPI API key
- `JWT_SECRET` - Generate with: `openssl rand -base64 32`
- `HOMEASSISTANT_URL` - Your HA instance URL
- `HOMEASSISTANT_WEBHOOK_ID` - Your HA webhook ID

Save: `Ctrl+X`, `Y`, `Enter`

### 7. Create Simplified Docker Compose (HTTP Only)

```bash
cat > docker-compose-http.yml << 'EOF'
version: '3.8'

services:
  webhook:
    build:
      context: ./webhook_service
      dockerfile: Dockerfile
    container_name: vapi-webhook
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - VAPI_API_KEY=${VAPI_API_KEY}
      - VAPI_ASSISTANT_ID=${VAPI_ASSISTANT_ID}
      - JWT_SECRET=${JWT_SECRET}
      - HOMEASSISTANT_URL=${HOMEASSISTANT_URL:-https://ut-demo-urbanjungle.homeadapt.us}
      - HOMEASSISTANT_WEBHOOK_ID=${HOMEASSISTANT_WEBHOOK_ID:-vapi_air_circulator}
      - PORT=8001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
```

### 8. Start the Service

```bash
# Build and start
docker-compose -f docker-compose-http.yml build
docker-compose -f docker-compose-http.yml up -d

# Check status
docker-compose -f docker-compose-http.yml ps

# View logs
docker-compose -f docker-compose-http.yml logs -f webhook
```

### 9. Configure Firewall

```bash
# Install UFW
apt-get install -y ufw

# Allow SSH, HTTP, and port 8001
ufw allow OpenSSH
ufw allow 8001/tcp

# Enable firewall
ufw --force enable
ufw status
```

### 10. Test the Webhook

```bash
# Test locally on droplet
curl http://localhost:8001/health

# Should return: {"status":"healthy"}
```

From your computer:
```bash
# From Windows PowerShell
Invoke-RestMethod -Uri "http://YOUR_DROPLET_IP:8001/health"

# From Linux/Mac
curl http://YOUR_DROPLET_IP:8001/health
```

### 11. Update VAPI Assistant Configuration

Go to [VAPI Dashboard](https://dashboard.vapi.ai/) and update your assistant:

**Server URL:**
```
http://YOUR_DROPLET_IP:8001/webhook?device_id={{device_id}}
```

**Important:** Replace `YOUR_DROPLET_IP` with your actual droplet IP address.

Example:
```
http://157.245.123.45:8001/webhook?device_id={{device_id}}
```

## Management Commands

### View Logs
```bash
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml logs -f webhook
```

### Restart Service
```bash
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml restart
```

### Stop Service
```bash
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml down
```

### Update Deployment
```bash
cd /opt/secure_voice
git pull
docker-compose -f docker-compose-http.yml up -d --build
```

### Check Service Status
```bash
cd /opt/secure_voice
docker-compose -f docker-compose-http.yml ps
```

## Test Authentication

```bash
# Test device authentication
curl -X POST http://YOUR_DROPLET_IP:8001/device/auth \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "pi_test_001",
    "device_secret": "test_secret"
  }'
```

## From Windows

```powershell
# Test health
Invoke-RestMethod -Uri "http://YOUR_DROPLET_IP:8001/health"

# Test authentication
$body = @{
    device_id = "pi_test_001"
    device_secret = "test_secret"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://YOUR_DROPLET_IP:8001/device/auth" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## Security Note

**⚠️ HTTP vs HTTPS:**

This deployment uses HTTP (not HTTPS) because you don't have a domain for SSL certificates.

**Risks:**
- Traffic is not encrypted
- API keys visible in transit
- Not recommended for production

**Mitigation:**
- Use only for testing/development
- Deploy behind VPN if possible
- Get a domain and setup SSL for production

**To add HTTPS later:**
1. Get a domain name
2. Point domain to your droplet IP
3. Use full `docker-compose.yml` with nginx and certbot
4. Follow `DEPLOYMENT_DIGITALOCEAN.md` SSL setup

## Alternative: Use Cloudflare Tunnel (Free SSL)

If you want HTTPS without a domain, use Cloudflare Tunnel:

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create vapi-webhook

# Configure tunnel
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: vapi-webhook
credentials-file: /root/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: webhook.your-cloudflare-domain.com
    service: http://localhost:8001
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel run vapi-webhook
```

This gives you HTTPS for free without buying a domain.

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose -f docker-compose-http.yml up -d` | Start services |
| `docker-compose -f docker-compose-http.yml down` | Stop services |
| `docker-compose -f docker-compose-http.yml restart` | Restart services |
| `docker-compose -f docker-compose-http.yml logs -f` | View logs |
| `docker-compose -f docker-compose-http.yml ps` | Check status |
| `curl http://localhost:8001/health` | Test health |

## Your Webhook URLs

Replace `YOUR_DROPLET_IP` with your actual IP address:

- **Health:** `http://YOUR_DROPLET_IP:8001/health`
- **Auth:** `http://YOUR_DROPLET_IP:8001/device/auth`
- **VAPI Config:** `http://YOUR_DROPLET_IP:8001/device/vapi-config`
- **Webhook:** `http://YOUR_DROPLET_IP:8001/webhook?device_id={{device_id}}`

## Troubleshooting

### Can't connect to webhook

```bash
# Check if service is running
docker-compose -f docker-compose-http.yml ps

# Check logs
docker-compose -f docker-compose-http.yml logs webhook

# Check firewall
ufw status

# Make sure port 8001 is allowed
ufw allow 8001/tcp
```

### Service won't start

```bash
# Check environment variables
cat .env

# Rebuild container
docker-compose -f docker-compose-http.yml build --no-cache
docker-compose -f docker-compose-http.yml up -d
```

### VAPI can't reach webhook

```bash
# Make sure firewall allows inbound connections
ufw allow 8001/tcp

# Test from external network
curl http://YOUR_DROPLET_IP:8001/health
```

If it works locally but not from VAPI, check Digital Ocean firewall settings in the web console.

## Upgrade to HTTPS Later

When you get a domain:

1. Point domain to droplet IP
2. Use full `docker-compose.yml`:
   ```bash
   docker-compose -f docker-compose-http.yml down
   docker-compose up -d
   ```
3. Setup SSL with certbot
4. Update VAPI to use `https://yourdomain.com/webhook?device_id={{device_id}}`

See `DEPLOYMENT_DIGITALOCEAN.md` for full HTTPS setup.
