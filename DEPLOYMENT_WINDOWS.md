# Deploy to Digital Ocean from Windows

Complete guide for Windows users to deploy the VAPI Secure Webhook service to Digital Ocean using Docker.

## Prerequisites

### Windows Requirements

1. **Windows 10/11** (64-bit)
2. **PowerShell 5.1+** (included in Windows 10/11)
3. **SSH Client** (OpenSSH)
4. **Git for Windows** (optional but recommended)

### Digital Ocean Requirements

1. Digital Ocean account
2. Domain name (optional but recommended for SSL)
3. VAPI API key and Assistant ID

## Installation Steps

### 1. Install OpenSSH Client (if not already installed)

**Option A: Via Windows Settings**
```
Settings → Apps → Optional Features → Add a feature → OpenSSH Client → Install
```

**Option B: Via PowerShell (Run as Administrator)**
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

Verify installation:
```powershell
ssh -V
# Should show: OpenSSH_for_Windows_8.x
```

### 2. Setup SSH Key

**Generate SSH Key (if you don't have one)**
```powershell
# Open PowerShell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for default location: C:\Users\YourName\.ssh\id_ed25519
# Set a passphrase or press Enter for no passphrase
```

**View Your Public Key**
```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
# Or use notepad
notepad $env:USERPROFILE\.ssh\id_ed25519.pub
```

**Add SSH Key to Digital Ocean**
1. Copy your public key content
2. Go to Digital Ocean → Settings → Security → SSH Keys
3. Click "Add SSH Key"
4. Paste your public key and give it a name
5. Click "Add SSH Key"

### 3. Create Digital Ocean Droplet

**Option A: Via Digital Ocean Web Console**

1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Click "Create" → "Droplets"
3. Choose:
   - **Distribution**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/month - 2GB RAM recommended)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH keys (select your key)
   - **Hostname**: vapi-webhook
4. Click "Create Droplet"
5. Note the droplet IP address

**Option B: Via doctl CLI (Windows)**

Install doctl:
```powershell
# Using winget (Windows 10/11)
winget install DigitalOcean.doctl

# Or using Chocolatey
choco install doctl

# Authenticate
doctl auth init
# Enter your Digital Ocean API token
```

Create droplet:
```powershell
doctl compute droplet create vapi-webhook `
  --image ubuntu-22-04-x64 `
  --size s-2vcpu-2gb `
  --region nyc1 `
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header)
```

### 4. Point Domain to Droplet (Optional)

If you have a domain:

1. Get your droplet IP from Digital Ocean console
2. In your domain registrar (Cloudflare, GoDaddy, Namecheap, etc.):
   - Create an **A record**
   - Name: `webhook` (or `@` for root domain)
   - Content/Value: `YOUR_DROPLET_IP`
   - TTL: Automatic or 3600
3. Wait 5-30 minutes for DNS propagation

Verify DNS:
```powershell
nslookup webhook.yourdomain.com
```

## Deployment Methods

### Method 1: PowerShell Script (Recommended)

**Step 1: Download Repository**
```powershell
# Clone repository
cd $env:USERPROFILE\Downloads
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice

# Or download ZIP and extract
```

**Step 2: Run Deployment Script**
```powershell
# Basic deployment (HTTP only)
.\deploy-to-do.ps1 -DropletIP YOUR_DROPLET_IP

# With domain (for HTTPS/SSL)
.\deploy-to-do.ps1 -DropletIP YOUR_DROPLET_IP -Domain webhook.yourdomain.com
```

Example:
```powershell
.\deploy-to-do.ps1 -DropletIP 192.168.1.100 -Domain webhook.example.com
```

**Step 3: Configure Environment**

SSH into your droplet:
```powershell
ssh root@YOUR_DROPLET_IP
```

Edit configuration:
```bash
nano /opt/secure_voice/.env
```

Update these values:
```bash
VAPI_API_KEY=your_actual_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138
JWT_SECRET=$(openssl rand -base64 32)
HOMEASSISTANT_URL=https://your-ha-instance.com
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator
DOMAIN=webhook.yourdomain.com
```

Save: `Ctrl+X`, `Y`, `Enter`

**Step 4: Start Services**
```bash
cd /opt/secure_voice
docker-compose up -d
```

**Step 5: Verify Deployment**
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f webhook

# Test health endpoint
curl http://localhost:8001/health
```

Exit SSH: `exit`

### Method 2: Manual SSH Commands (Windows PowerShell)

**Step 1: Connect to Droplet**
```powershell
ssh root@YOUR_DROPLET_IP
```

**Step 2: Install Docker and Docker Compose**
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

**Step 3: Clone Repository**
```bash
mkdir -p /opt/secure_voice
cd /opt/secure_voice
git clone https://github.com/karthi1975/secure_voice.git .
```

**Step 4: Configure Environment**
```bash
# Copy example .env
cp .env.example .env

# Edit .env
nano .env
```

Update:
```bash
VAPI_API_KEY=your_vapi_api_key_here
JWT_SECRET=$(openssl rand -base64 32)
DOMAIN=webhook.yourdomain.com
```

**Step 5: Update Nginx Config**
```bash
# Replace domain in nginx config
sed -i 's/your-domain.com/webhook.yourdomain.com/g' nginx/conf.d/webhook.conf
```

**Step 6: Start Services**
```bash
cd /opt/secure_voice
docker-compose up -d
```

**Step 7: Setup SSL Certificate**
```bash
# Create directories
mkdir -p certbot/conf certbot/www

# Get certificate
docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@yourdomain.com \
    --agree-tos \
    --no-eff-email \
    -d webhook.yourdomain.com

# Restart nginx
docker-compose restart nginx
```

**Step 8: Configure Firewall**
```bash
apt-get install -y ufw
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### Method 3: Using WSL (Windows Subsystem for Linux)

If you prefer using Linux bash scripts on Windows:

**Step 1: Install WSL**
```powershell
# Run as Administrator
wsl --install
# Restart computer
```

**Step 2: Open WSL Terminal**
```powershell
wsl
```

**Step 3: Follow Linux Instructions**
```bash
# Now you can use the Linux deployment script
cd /mnt/c/Users/YourName/Downloads/secure_voice
chmod +x deploy-to-do.sh
./deploy-to-do.sh
```

## Using Windows Terminal (Recommended)

Windows Terminal provides a better SSH experience:

### Install Windows Terminal
```powershell
# Via Microsoft Store
# Search for "Windows Terminal" and install

# Or via winget
winget install Microsoft.WindowsTerminal
```

### Connect to Droplet
```powershell
# Open Windows Terminal
# Click "+" → PowerShell or Command Prompt
ssh root@YOUR_DROPLET_IP
```

## Managing Deployment from Windows

### SSH Connection Profile (Windows Terminal)

Create a profile for easy access:

1. Open Windows Terminal
2. Settings (Ctrl+,)
3. Add new profile
4. Command line: `ssh root@YOUR_DROPLET_IP`
5. Name: "Digital Ocean - VAPI Webhook"
6. Save

### PowerShell Commands

**Connect to Droplet**
```powershell
ssh root@YOUR_DROPLET_IP
```

**View Logs**
```powershell
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose logs -f webhook"
```

**Restart Services**
```powershell
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose restart"
```

**Update Deployment**
```powershell
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && git pull && docker-compose up -d --build"
```

**Check Health**
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "https://webhook.yourdomain.com/health" | Select-Object -ExpandProperty Content
```

### Using PuTTY (Alternative SSH Client)

If you prefer PuTTY:

1. **Download PuTTY**: https://www.putty.org/
2. **Install PuTTY**
3. **Convert SSH Key** (if using key authentication):
   - Open PuTTYgen
   - Load your private key (id_ed25519)
   - Save private key as `.ppk` format
4. **Connect**:
   - Host: `root@YOUR_DROPLET_IP`
   - Port: 22
   - Connection → SSH → Auth: Browse to your `.ppk` file
   - Click "Open"

### Using WinSCP (File Transfer)

To transfer files between Windows and droplet:

1. **Download WinSCP**: https://winscp.net/
2. **Install WinSCP**
3. **Connect**:
   - Protocol: SFTP
   - Host: YOUR_DROPLET_IP
   - Username: root
   - Private key: Browse to your `.ppk` file
4. **Transfer files** using drag-and-drop

## Monitoring from Windows

### PowerShell Monitoring Script

Create `monitor.ps1`:
```powershell
param(
    [string]$DropletIP = "YOUR_DROPLET_IP"
)

Write-Host "Monitoring VAPI Webhook Service" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    try {
        $response = Invoke-WebRequest -Uri "http://$DropletIP:8001/health" -TimeoutSec 5
        $status = $response.StatusCode

        if ($status -eq 200) {
            Write-Host "[$timestamp] Status: OK ($status)" -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] Status: WARNING ($status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[$timestamp] Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }

    Start-Sleep -Seconds 30
}
```

Run:
```powershell
.\monitor.ps1 -DropletIP YOUR_DROPLET_IP
```

## Troubleshooting Windows-Specific Issues

### SSH Connection Issues

**Problem: "Connection refused"**
```powershell
# Check if SSH service is running on droplet
ssh -v root@YOUR_DROPLET_IP
```

**Problem: "Permission denied (publickey)"**
```powershell
# Use password authentication (if enabled)
ssh -o PreferredAuthentications=password root@YOUR_DROPLET_IP

# Or specify private key
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@YOUR_DROPLET_IP
```

**Problem: "Host key verification failed"**
```powershell
# Remove old host key
ssh-keygen -R YOUR_DROPLET_IP
```

### PowerShell Execution Policy

If scripts won't run:
```powershell
# Check current policy
Get-ExecutionPolicy

# Allow scripts (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Firewall Issues

**Windows Firewall blocking SSH**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "SSH Outbound" -Direction Outbound -Protocol TCP -LocalPort 22 -Action Allow
```

### Line Ending Issues

If you edit files on Windows and upload to Linux:

**Convert CRLF to LF**
```powershell
# Using Git
git config --global core.autocrlf input

# Or in VSCode
# Bottom right: CRLF → LF
```

## Testing Deployment

### From Windows PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/health"

# Test authentication
$body = @{
    device_id = "pi_test_001"
    device_secret = "test_secret"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://webhook.yourdomain.com/device/auth" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Test VAPI config endpoint
$token = "YOUR_JWT_TOKEN"
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/device/vapi-config" `
    -Headers @{Authorization = "Bearer $token"}
```

### From Command Prompt (cmd.exe)

```cmd
REM Health check
curl https://webhook.yourdomain.com/health

REM Test authentication
curl -X POST https://webhook.yourdomain.com/device/auth ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"pi_test_001\",\"device_secret\":\"test_secret\"}"
```

## Quick Reference Commands

### Connection
```powershell
# SSH to droplet
ssh root@YOUR_DROPLET_IP

# SSH with specific key
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@YOUR_DROPLET_IP
```

### Service Management
```powershell
# Start services
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose up -d"

# Stop services
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose down"

# Restart services
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose restart"

# View logs
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose logs -f webhook"

# Check status
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose ps"
```

### Updates
```powershell
# Update code and rebuild
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && git pull && docker-compose up -d --build"
```

## File Editing on Windows

### Option 1: VSCode with Remote SSH Extension

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install "Remote - SSH" extension
3. Connect to droplet:
   - Press `F1`
   - Type "Remote-SSH: Connect to Host"
   - Enter `root@YOUR_DROPLET_IP`
4. Open folder: `/opt/secure_voice`
5. Edit files directly

### Option 2: Edit Locally, Upload via SCP

```powershell
# Edit .env locally
notepad .env

# Upload to droplet
scp .env root@YOUR_DROPLET_IP:/opt/secure_voice/.env

# Restart services
ssh root@YOUR_DROPLET_IP "cd /opt/secure_voice && docker-compose restart"
```

### Option 3: Nano via SSH

```powershell
ssh root@YOUR_DROPLET_IP
nano /opt/secure_voice/.env
# Edit, Ctrl+X, Y, Enter
exit
```

## Next Steps

After deployment:

1. **Update VAPI Assistant**:
   - Go to [VAPI Dashboard](https://dashboard.vapi.ai/)
   - Select your assistant
   - Update **Server URL** to:
     ```
     https://webhook.yourdomain.com/webhook?device_id={{device_id}}
     ```

2. **Configure Multi-Tenant** (if needed):
   - Edit device mappings in `webhook_service/device_auth.py`
   - Edit HA instances in `webhook_service/ha_instances.py`
   - Restart services

3. **Setup Monitoring** (optional):
   - Use provided PowerShell monitoring script
   - Or setup UptimeRobot/Pingdom for external monitoring

## Support

- **GitHub Issues**: https://github.com/karthi1975/secure_voice/issues
- **Documentation**: See README.md and ARCHITECTURE.md
- **Windows Terminal Docs**: https://docs.microsoft.com/en-us/windows/terminal/

## Common Windows Tools

- **SSH Client**: Built-in OpenSSH or PuTTY
- **File Transfer**: WinSCP, FileZilla
- **Code Editor**: VSCode with Remote-SSH, Notepad++
- **Terminal**: Windows Terminal (recommended)
- **Package Manager**: winget, Chocolatey (optional)

## License

MIT
