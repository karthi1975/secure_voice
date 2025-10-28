# Deploy VAPI Webhook with IP Address Only (No Domain)
# PowerShell Script for Windows Users

param(
    [Parameter(Mandatory=$true)]
    [string]$DropletIP,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Deploy VAPI Webhook - IP Only (No Domain)

Usage:
    .\deploy-ip-only.ps1 -DropletIP <IP>

Parameters:
    -DropletIP    IP address of your Digital Ocean droplet (required)
    -Help         Show this help message

Example:
    .\deploy-ip-only.ps1 -DropletIP 192.168.1.100

"@
    exit
}

$SSHUser = "root"

Write-Host "========================================" -ForegroundColor Green
Write-Host "VAPI Webhook - IP Only Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Droplet IP: $DropletIP" -ForegroundColor Cyan
Write-Host ""

# Check SSH
try {
    $null = Get-Command ssh -ErrorAction Stop
    Write-Host "[OK] SSH client found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] SSH client not found" -ForegroundColor Red
    Write-Host "Install: Settings -> Apps -> Optional Features -> OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

# Test connection
Write-Host ""
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes $SSHUser@$DropletIP "echo connected" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Cannot connect with SSH key" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "[OK] SSH connection successful" -ForegroundColor Green
}

Write-Host ""
Write-Host "Uploading deployment script..." -ForegroundColor Yellow

# Create deployment script
$deployScript = @"
#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\${GREEN}========================================\${NC}"
echo -e "\${GREEN}VAPI Webhook - IP Only Deployment\${NC}"
echo -e "\${GREEN}========================================\${NC}"
echo ""

DROPLET_IP=\$(curl -s ifconfig.me)
echo -e "\${BLUE}Droplet IP: \${GREEN}\$DROPLET_IP\${NC}"
echo ""

# Update system
echo -e "\${YELLOW}Step 1/8: Updating system...\${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update > /dev/null 2>&1
apt-get upgrade -y > /dev/null 2>&1
echo -e "\${GREEN}✓ System updated\${NC}"

# Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "\${YELLOW}Step 2/8: Installing Docker...\${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    systemctl enable docker > /dev/null 2>&1
    systemctl start docker
    echo -e "\${GREEN}✓ Docker installed\${NC}"
else
    echo -e "\${GREEN}✓ Docker already installed\${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "\${YELLOW}Step 3/8: Installing Docker Compose...\${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "\${GREEN}✓ Docker Compose installed\${NC}"
else
    echo -e "\${GREEN}✓ Docker Compose already installed\${NC}"
fi

# Setup app directory
APP_DIR="/opt/secure_voice"
echo -e "\${YELLOW}Step 4/8: Setting up application...\${NC}"
mkdir -p \$APP_DIR
cd \$APP_DIR

if [ -d ".git" ]; then
    git pull > /dev/null 2>&1
else
    git clone https://github.com/karthi1975/secure_voice.git . > /dev/null 2>&1
fi
echo -e "\${GREEN}✓ Repository ready\${NC}"

# Create .env
echo -e "\${YELLOW}Step 5/8: Creating environment file...\${NC}"
if [ ! -f ".env" ]; then
    JWT_SECRET=\$(openssl rand -base64 32)
    cat > .env << 'ENVEOF'
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138
JWT_SECRET=\$JWT_SECRET
HOMEASSISTANT_URL=https://ut-demo-urbanjungle.homeadapt.us
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator
PORT=8001
ENVEOF
    echo -e "\${GREEN}✓ .env created\${NC}"
else
    echo -e "\${GREEN}✓ .env exists\${NC}"
fi

# Create docker-compose
echo -e "\${YELLOW}Step 6/8: Creating Docker configuration...\${NC}"
cat > docker-compose-http.yml << 'DCEOF'
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
      - VAPI_API_KEY=\${VAPI_API_KEY}
      - VAPI_ASSISTANT_ID=\${VAPI_ASSISTANT_ID}
      - JWT_SECRET=\${JWT_SECRET}
      - HOMEASSISTANT_URL=\${HOMEASSISTANT_URL}
      - HOMEASSISTANT_WEBHOOK_ID=\${HOMEASSISTANT_WEBHOOK_ID}
      - PORT=8001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
DCEOF
echo -e "\${GREEN}✓ Docker config created\${NC}"

# Firewall
echo -e "\${YELLOW}Step 7/8: Configuring firewall...\${NC}"
if command -v ufw &> /dev/null; then
    ufw --force enable > /dev/null 2>&1
    ufw allow OpenSSH > /dev/null 2>&1
    ufw allow 8001/tcp > /dev/null 2>&1
    echo -e "\${GREEN}✓ Firewall configured\${NC}"
fi

# Start services
echo -e "\${YELLOW}Step 8/8: Building and starting services...\${NC}"
docker-compose -f docker-compose-http.yml build > /dev/null 2>&1
docker-compose -f docker-compose-http.yml up -d

sleep 10

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "\${GREEN}✓ Service healthy\${NC}"
else
    echo -e "\${RED}✗ Health check failed\${NC}"
fi

echo ""
echo -e "\${GREEN}========================================\${NC}"
echo -e "\${GREEN}Deployment Complete!\${NC}"
echo -e "\${GREEN}========================================\${NC}"
echo ""
echo -e "\${BLUE}Your Webhook URL:\${NC}"
echo -e "  \${GREEN}http://\$DROPLET_IP:8001/webhook?device_id={{device_id}}\${NC}"
echo ""
echo -e "\${YELLOW}Next Steps:\${NC}"
echo -e "  1. Edit .env: nano /opt/secure_voice/.env"
echo -e "  2. Update VAPI_API_KEY"
echo -e "  3. Restart: docker-compose -f docker-compose-http.yml restart"
echo -e "  4. Update VAPI Assistant with webhook URL above"
echo ""
"@

# Upload and run
Write-Host "Running deployment on droplet..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

$deployScript | ssh $SSHUser@$DropletIP "cat > /tmp/deploy-ip.sh && chmod +x /tmp/deploy-ip.sh && bash /tmp/deploy-ip.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Webhook URL:" -ForegroundColor Cyan
    Write-Host "  http://$DropletIP:8001/webhook?device_id={{device_id}}" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT - Next Steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Edit configuration:" -ForegroundColor Cyan
    Write-Host "   ssh root@$DropletIP" -ForegroundColor White
    Write-Host "   nano /opt/secure_voice/.env" -ForegroundColor White
    Write-Host "   Update: VAPI_API_KEY=your_actual_key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Restart service:" -ForegroundColor Cyan
    Write-Host "   cd /opt/secure_voice" -ForegroundColor White
    Write-Host "   docker-compose -f docker-compose-http.yml restart" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Test webhook:" -ForegroundColor Cyan
    Write-Host "   Invoke-RestMethod -Uri http://$DropletIP:8001/health" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Update VAPI Assistant Server URL to:" -ForegroundColor Cyan
    Write-Host "   http://$DropletIP:8001/webhook?device_id={{device_id}}" -ForegroundColor Green
    Write-Host ""
    Write-Host "WARNING: HTTP only (no encryption)" -ForegroundColor Red
    Write-Host "OK for testing, use HTTPS for production" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Deployment failed! Check errors above." -ForegroundColor Red
    exit 1
}
