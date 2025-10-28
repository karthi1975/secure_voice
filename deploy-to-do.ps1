# Deploy VAPI Webhook to Digital Ocean Droplet from Windows
# PowerShell Script for Windows Users

param(
    [string]$DropletIP = "",
    [string]$Domain = "localhost",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Deploy VAPI Webhook to Digital Ocean

Usage:
    .\deploy-to-do.ps1 -DropletIP <IP> [-Domain <domain>]

Parameters:
    -DropletIP    IP address of your Digital Ocean droplet (required)
    -Domain       Domain name for SSL certificate (optional)
    -Help         Show this help message

Examples:
    .\deploy-to-do.ps1 -DropletIP 192.168.1.100
    .\deploy-to-do.ps1 -DropletIP 192.168.1.100 -Domain webhook.example.com

"@
    exit
}

if ([string]::IsNullOrEmpty($DropletIP)) {
    Write-Host "Error: DropletIP is required" -ForegroundColor Red
    Write-Host "Usage: .\deploy-to-do.ps1 -DropletIP <IP> [-Domain <domain>]" -ForegroundColor Yellow
    exit 1
}

# Configuration
$AppDir = "/opt/secure_voice"
$RepoUrl = "https://github.com/karthi1975/secure_voice.git"
$SSHUser = "root"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Deploy to Digital Ocean - Windows" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Droplet IP: $DropletIP" -ForegroundColor Cyan
Write-Host "Domain: $Domain" -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
try {
    $null = Get-Command ssh -ErrorAction Stop
    Write-Host "[OK] SSH client found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] SSH client not found" -ForegroundColor Red
    Write-Host "Please install OpenSSH client:" -ForegroundColor Yellow
    Write-Host "  Settings -> Apps -> Optional Features -> Add OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

# Check if we can connect to the droplet
Write-Host ""
Write-Host "Testing SSH connection to droplet..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes $SSHUser@$DropletIP "echo connected" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Cannot connect to droplet with SSH key" -ForegroundColor Yellow
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "  1. Added your SSH public key to Digital Ocean" -ForegroundColor Yellow
    Write-Host "  2. SSH key is loaded in ssh-agent" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "[OK] SSH connection successful" -ForegroundColor Green
}

# Create deployment script
Write-Host ""
Write-Host "Creating deployment script on droplet..." -ForegroundColor Yellow

$deployScript = @"
#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\${YELLOW}Starting deployment....\${NC}"

# Update system
echo -e "\${YELLOW}Updating system packages...\${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "\${YELLOW}Installing Docker...\${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "\${GREEN}Docker installed\${NC}"
else
    echo -e "\${GREEN}Docker already installed\${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "\${YELLOW}Installing Docker Compose...\${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "\${GREEN}Docker Compose installed\${NC}"
else
    echo -e "\${GREEN}Docker Compose already installed\${NC}"
fi

# Create app directory
mkdir -p $AppDir
cd $AppDir

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "\${YELLOW}Updating repository...\${NC}"
    git pull
else
    echo -e "\${YELLOW}Cloning repository...\${NC}"
    git clone $RepoUrl .
fi

# Create .env file if doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\${YELLOW}Creating .env file...\${NC}"
    cp .env.example .env
    echo -e "\${RED}IMPORTANT: Edit .env file with your credentials!\${NC}"
fi

# Update nginx domain
if [ "$Domain" != "localhost" ]; then
    echo -e "\${YELLOW}Updating nginx configuration with domain: $Domain\${NC}"
    sed -i "s/your-domain.com/$Domain/g" nginx/conf.d/webhook.conf
fi

# Create certbot directories
mkdir -p certbot/conf certbot/www

# Configure firewall
if command -v ufw &> /dev/null; then
    echo -e "\${YELLOW}Configuring firewall...\${NC}"
    ufw --force enable
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo -e "\${GREEN}Firewall configured\${NC}"
fi

echo -e "\${GREEN}Deployment preparation complete!\${NC}"
echo -e "\${YELLOW}Next steps:\${NC}"
echo -e "  1. Edit .env file: nano $AppDir/.env"
echo -e "  2. Start services: cd $AppDir && docker-compose up -d"
"@

# Upload and run deployment script
Write-Host "Uploading deployment script..." -ForegroundColor Yellow
$deployScript | ssh $SSHUser@$DropletIP "cat > /tmp/deploy.sh"
ssh $SSHUser@$DropletIP "chmod +x /tmp/deploy.sh"

Write-Host ""
Write-Host "Running deployment script on droplet..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

ssh $SSHUser@$DropletIP "bash /tmp/deploy.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Connect to your droplet:" -ForegroundColor Cyan
    Write-Host "   ssh root@$DropletIP" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Edit the .env file:" -ForegroundColor Cyan
    Write-Host "   nano $AppDir/.env" -ForegroundColor White
    Write-Host ""
    Write-Host "   Update these variables:" -ForegroundColor Yellow
    Write-Host "   - VAPI_API_KEY=your_actual_key" -ForegroundColor White
    Write-Host "   - JWT_SECRET=`$(openssl rand -base64 32)" -ForegroundColor White
    Write-Host "   - DOMAIN=$Domain" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Start the services:" -ForegroundColor Cyan
    Write-Host "   cd $AppDir" -ForegroundColor White
    Write-Host "   docker-compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Check service status:" -ForegroundColor Cyan
    Write-Host "   docker-compose ps" -ForegroundColor White
    Write-Host "   docker-compose logs -f webhook" -ForegroundColor White
    Write-Host ""

    if ($Domain -ne "localhost") {
        Write-Host "5. Access your webhook at:" -ForegroundColor Cyan
        Write-Host "   https://$Domain" -ForegroundColor Green
        Write-Host ""
        Write-Host "6. Update VAPI webhook URL to:" -ForegroundColor Cyan
        Write-Host "   https://$Domain/webhook?device_id={{device_id}}" -ForegroundColor Green
    } else {
        Write-Host "5. Access your webhook at:" -ForegroundColor Cyan
        Write-Host "   http://$DropletIP:8001" -ForegroundColor Green
    }
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Deployment failed! Check the error messages above." -ForegroundColor Red
    exit 1
}
