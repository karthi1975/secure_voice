# Deploy to Digital Ocean with Docker

Complete guide to deploy the VAPI Secure Webhook service to Digital Ocean using Docker.

## Prerequisites

- Digital Ocean account
- Domain name (optional but recommended for SSL)
- VAPI API key and Assistant ID
- SSH access to your droplet

## Quick Start

### 1. Create Digital Ocean Droplet

**Option A: Via Digital Ocean Web Console**

1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Click "Create" → "Droplets"
3. Choose configuration:
   - **Distribution**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month or $12/month recommended)
   - **CPU**: Regular (1-2 vCPU)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH key (recommended) or password
4. Add your SSH key or set root password
5. Click "Create Droplet"

**Option B: Via doctl CLI**

```bash
# Install doctl
brew install doctl  # macOS
# or download from https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create droplet
doctl compute droplet create vapi-webhook \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-2gb \
  --region nyc1 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header)
```

### 2. Point Domain to Droplet (Optional but Recommended)

1. Get your droplet IP: `doctl compute droplet list` or from DO console
2. In your domain registrar (Cloudflare, GoDaddy, etc.):
   - Create an **A record** pointing to your droplet IP
   - Example: `webhook.yourdomain.com` → `YOUR_DROPLET_IP`
3. Wait for DNS propagation (5-30 minutes)

### 3. SSH into Droplet

```bash
# Get droplet IP
doctl compute droplet list

# SSH into droplet
ssh root@YOUR_DROPLET_IP
```

### 4. Run Automated Deployment Script

```bash
# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/karthi1975/secure_voice/main/deploy-to-do.sh -o deploy-to-do.sh
chmod +x deploy-to-do.sh
sudo ./deploy-to-do.sh
```

The script will:
- Install Docker and Docker Compose
- Clone the repository
- Create `.env` configuration file
- Setup nginx reverse proxy
- Configure SSL with Let's Encrypt (if domain provided)
- Start all services

### 5. Configure Environment Variables

Edit the `.env` file:

```bash
nano /opt/secure_voice/.env
```

Update the following variables:

```bash
# VAPI Configuration
VAPI_API_KEY=your_actual_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138

# JWT Secret (generate a secure random string)
JWT_SECRET=$(openssl rand -base64 32)

# Home Assistant Configuration
HOMEASSISTANT_URL=https://your-ha-instance.com
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator

# Domain (for SSL)
DOMAIN=webhook.yourdomain.com
```

Save and exit (Ctrl+X, Y, Enter)

### 6. Restart Services

```bash
cd /opt/secure_voice
docker-compose down
docker-compose up -d
```

### 7. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f webhook

# Test health endpoint
curl http://localhost:8001/health

# Test external access
curl https://webhook.yourdomain.com/health
```

Expected response: `{"status":"healthy"}`

## Manual Deployment Steps

If you prefer manual control:

### 1. Install Docker and Docker Compose

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

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Repository

```bash
mkdir -p /opt/secure_voice
cd /opt/secure_voice
git clone https://github.com/karthi1975/secure_voice.git .
```

### 3. Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138
JWT_SECRET=$(openssl rand -base64 32)
HOMEASSISTANT_URL=https://ut-demo-urbanjungle.homeadapt.us
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator
DOMAIN=webhook.yourdomain.com
EOF

# Edit with your actual values
nano .env
```

### 4. Update Nginx Configuration

```bash
# Update domain in nginx config
sed -i 's/your-domain.com/webhook.yourdomain.com/g' nginx/conf.d/webhook.conf
```

### 5. Start Services (HTTP Only - For Testing)

```bash
# Start without SSL first
docker-compose up -d webhook

# Test health
curl http://localhost:8001/health
```

### 6. Setup SSL Certificate

```bash
# Create certbot directories
mkdir -p certbot/conf certbot/www

# Temporarily modify nginx for HTTP-only
cp nginx/conf.d/webhook.conf nginx/conf.d/webhook.conf.bak
cat > nginx/conf.d/webhook.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://webhook:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Start nginx
docker-compose up -d nginx

# Get SSL certificate
docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@yourdomain.com \
    --agree-tos \
    --no-eff-email \
    -d webhook.yourdomain.com

# Restore HTTPS config
mv nginx/conf.d/webhook.conf.bak nginx/conf.d/webhook.conf

# Restart nginx
docker-compose restart nginx
```

### 7. Configure Firewall

```bash
# Install and configure UFW
apt-get install -y ufw

# Allow SSH, HTTP, HTTPS
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable
ufw status
```

### 8. Start All Services

```bash
docker-compose up -d
```

## Architecture

```
                     ┌─────────────────┐
                     │ Digital Ocean   │
                     │   Droplet       │
                     │  (Ubuntu 22.04) │
                     └────────┬────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Docker Host     │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  ┌─────▼─────┐      ┌────────▼────────┐   ┌───────▼────────┐
  │   Nginx   │      │ Webhook Service │   │    Certbot     │
  │  (Port 80 │◄─────┤   (FastAPI)     │   │ (SSL Renewal)  │
  │  Port 443)│      │   (Port 8001)   │   └────────────────┘
  └───────────┘      └─────────────────┘
       │
       │ HTTPS
       ▼
  ┌──────────┐
  │   VAPI   │
  │  Client  │
  └──────────┘
```

## Configuration Files

### docker-compose.yml

The compose file defines:
- **webhook**: FastAPI service on port 8001
- **nginx**: Reverse proxy on ports 80/443
- **certbot**: SSL certificate renewal

### Dockerfile

Multi-stage build:
1. Python 3.11 slim base
2. Install dependencies
3. Copy application code
4. Run as non-root user

### nginx Configuration

- HTTP → HTTPS redirect
- WebSocket support
- Security headers
- SSL termination
- Proxy to webhook service

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VAPI_API_KEY` | Your VAPI public API key | `6ef83504-...` |
| `VAPI_ASSISTANT_ID` | VAPI assistant ID | `31377f1e-...` |
| `JWT_SECRET` | Secret for JWT tokens | Random 32-byte string |
| `HOMEASSISTANT_URL` | Home Assistant URL | `https://ha.example.com` |
| `HOMEASSISTANT_WEBHOOK_ID` | HA webhook ID | `vapi_air_circulator` |
| `DOMAIN` | Your domain name | `webhook.yourdomain.com` |

## Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Webhook only
docker-compose logs -f webhook

# Nginx only
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 webhook
```

### Restart Services

```bash
# All services
docker-compose restart

# Webhook only
docker-compose restart webhook

# Rebuild and restart
docker-compose up -d --build
```

### Update Deployment

```bash
cd /opt/secure_voice
git pull
docker-compose down
docker-compose up -d --build
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop but keep data
docker-compose stop

# Stop and remove volumes
docker-compose down -v
```

### Check Service Health

```bash
# Container status
docker-compose ps

# Health check
curl http://localhost:8001/health

# External health check
curl https://webhook.yourdomain.com/health

# Test authentication
curl -X POST https://webhook.yourdomain.com/device/auth \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "pi_test_001",
    "device_secret": "test_secret"
  }'
```

### Monitor Resources

```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

## Update VAPI Configuration

After deployment, update your VAPI assistant:

1. Go to [VAPI Dashboard](https://dashboard.vapi.ai/)
2. Select your assistant
3. Update **Server URL** to:
   ```
   https://webhook.yourdomain.com/webhook?device_id={{device_id}}
   ```
4. Save changes

## Multi-Tenant Configuration

### Add New Customer

Edit `webhook_service/device_auth.py`:

```python
DEVICES = {
    "pi_newcustomer_001": {
        "device_secret": "dev_secret_newcustomer_xyz789",
        "customer_id": "newcustomer",
        "name": "New Customer Pi #1",
        "location": "Living Room"
    }
}
```

Edit `webhook_service/ha_instances.py`:

```python
HA_INSTANCES = {
    "newcustomer": {
        "ha_url": "https://newcustomer.homeadapt.us",
        "ha_webhook_id": "vapi_voice",
        "name": "New Customer Home"
    }
}
```

Restart services:

```bash
docker-compose restart webhook
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs webhook

# Check environment variables
docker-compose exec webhook env | grep VAPI

# Rebuild container
docker-compose up -d --build webhook
```

### SSL Certificate Issues

```bash
# Check certificate status
docker-compose run --rm certbot certificates

# Renew certificate manually
docker-compose run --rm certbot renew

# Test renewal
docker-compose run --rm certbot renew --dry-run
```

### Nginx 502 Bad Gateway

```bash
# Check if webhook service is running
docker-compose ps webhook

# Check webhook logs
docker-compose logs webhook

# Test webhook directly
curl http://localhost:8001/health

# Restart services
docker-compose restart
```

### Port Already in Use

```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting service (e.g., Apache)
sudo systemctl stop apache2

# Or change ports in docker-compose.yml
ports:
  - "8080:80"
  - "8443:443"
```

### Can't Connect to Webhook

```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check DNS
nslookup webhook.yourdomain.com

# Check if service is listening
sudo netstat -tlnp | grep 443
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services to free memory
docker-compose restart

# Limit memory in docker-compose.yml
services:
  webhook:
    deploy:
      resources:
        limits:
          memory: 512M
```

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong JWT_SECRET** - Generate with `openssl rand -base64 32`
3. **Keep Docker updated** - `apt-get update && apt-get upgrade docker-ce`
4. **Enable automatic security updates**:
   ```bash
   apt-get install unattended-upgrades
   dpkg-reconfigure --priority=low unattended-upgrades
   ```
5. **Use SSH key authentication** - Disable password auth
6. **Configure fail2ban** for SSH protection
7. **Regular backups** of configuration and data
8. **Monitor logs** for suspicious activity
9. **Keep SSL certificates renewed** - Certbot does this automatically

## Backup and Restore

### Backup

```bash
# Backup environment and config
tar -czf secure-voice-backup-$(date +%Y%m%d).tar.gz \
  /opt/secure_voice/.env \
  /opt/secure_voice/nginx \
  /opt/secure_voice/certbot/conf

# Download to local machine
scp root@YOUR_DROPLET_IP:/root/secure-voice-backup-*.tar.gz .
```

### Restore

```bash
# Upload backup
scp secure-voice-backup-*.tar.gz root@YOUR_DROPLET_IP:/root/

# Extract
cd /
tar -xzf /root/secure-voice-backup-*.tar.gz

# Restart services
cd /opt/secure_voice
docker-compose up -d
```

## Performance Optimization

### Enable Caching

Add to nginx config:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=webhook_cache:10m max_size=100m;

location / {
    proxy_cache webhook_cache;
    proxy_cache_valid 200 1m;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
}
```

### Increase Worker Processes

Edit `nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 2048;
```

### Enable Connection Pooling

Add to webhook service environment:

```yaml
environment:
  - HTTPX_POOL_MAX_CONNECTIONS=100
```

## Monitoring

### Setup Logging

```bash
# View live logs
docker-compose logs -f

# Export logs to file
docker-compose logs > webhook-logs-$(date +%Y%m%d).log

# Setup log rotation
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker
```

### Health Monitoring

Create monitoring script `/root/check-health.sh`:

```bash
#!/bin/bash
if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "Webhook service unhealthy - restarting"
    cd /opt/secure_voice
    docker-compose restart webhook
fi
```

Add to crontab:

```bash
crontab -e
*/5 * * * * /root/check-health.sh
```

## Cost Optimization

- **$6/month**: Basic droplet (1 vCPU, 1GB RAM) - Good for testing
- **$12/month**: Standard droplet (1 vCPU, 2GB RAM) - Recommended for production
- **$18/month**: Enhanced droplet (2 vCPU, 2GB RAM) - High traffic

## Support

- **GitHub Issues**: https://github.com/karthi1975/secure_voice/issues
- **Documentation**: See README.md and ARCHITECTURE.md
- **VAPI Docs**: https://docs.vapi.ai

## License

MIT
