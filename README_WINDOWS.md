# 🪟 Windows Deployment Guide

Complete guide for deploying VAPI Secure Webhook to Digital Ocean from Windows.

## 📋 Table of Contents

- [Quick Start](#-quick-start-5-minutes)
- [Deployment Methods](#-deployment-methods)
- [Prerequisites](#-prerequisites)
- [Detailed Guides](#-detailed-guides)
- [Troubleshooting](#-troubleshooting)

## ⚡ Quick Start (5 minutes)

**For impatient Windows users:**

1. **Install OpenSSH** (if not installed):
   ```
   Settings → Apps → Optional Features → Add → OpenSSH Client → Install
   ```

2. **Generate SSH Key**:
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter 3 times
   ```

3. **Add SSH Key to Digital Ocean**:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
   # Copy output, paste at: https://cloud.digitalocean.com/account/security
   ```

4. **Create Droplet** at https://cloud.digitalocean.com/droplets
   - Ubuntu 22.04, $12/mo plan
   - Select your SSH key
   - Copy droplet IP

5. **Deploy**:
   ```powershell
   git clone https://github.com/karthi1975/secure_voice.git
   cd secure_voice
   .\deploy-to-do.ps1 -DropletIP YOUR_DROPLET_IP -Domain webhook.yourdomain.com
   ```

6. **Configure**:
   ```powershell
   ssh root@YOUR_DROPLET_IP
   nano /opt/secure_voice/.env
   # Update VAPI_API_KEY and JWT_SECRET
   cd /opt/secure_voice && docker-compose up -d
   ```

**Done!** 🎉

See [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md) for detailed quick start.

## 🚀 Deployment Methods

### Method 1: PowerShell Script (Recommended)

**Best for:** Most Windows users

```powershell
# Download repository
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice

# Deploy
.\deploy-to-do.ps1 -DropletIP YOUR_DROPLET_IP -Domain webhook.yourdomain.com
```

**Pros:**
- ✅ Fully automated
- ✅ Works on all Windows 10/11
- ✅ Best error handling

**See:** [deploy-to-do.ps1](deploy-to-do.ps1)

### Method 2: Batch Script

**Best for:** Users who prefer cmd.exe

```cmd
REM Download repository
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice

REM Deploy
deploy-windows.bat YOUR_DROPLET_IP webhook.yourdomain.com
```

**Pros:**
- ✅ Works in Command Prompt
- ✅ No PowerShell required
- ✅ Simple syntax

**See:** [deploy-windows.bat](deploy-windows.bat)

### Method 3: WSL (Windows Subsystem for Linux)

**Best for:** Developers familiar with Linux

```powershell
# Install WSL
wsl --install
# Restart computer

# Use Linux commands
wsl
cd /mnt/c/Users/YourName/Downloads/secure_voice
./deploy-to-do.sh
```

**Pros:**
- ✅ Use Linux bash scripts
- ✅ Full Linux environment
- ✅ Best compatibility

**See:** [DEPLOYMENT_DIGITALOCEAN.md](DEPLOYMENT_DIGITALOCEAN.md)

### Method 4: Manual SSH Commands

**Best for:** Advanced users who want control

```powershell
# Connect to droplet
ssh root@YOUR_DROPLET_IP

# Follow manual installation steps
# (Install Docker, clone repo, configure, start services)
```

**See:** [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md) - Manual Steps

## 📦 Prerequisites

### Required

| Item | Installation |
|------|-------------|
| **Windows 10/11** | Must be 64-bit |
| **PowerShell 5.1+** | Built-in |
| **OpenSSH Client** | Settings → Apps → Optional Features |
| **Digital Ocean Account** | Sign up at https://digitalocean.com |

### Optional but Recommended

| Tool | Purpose | Installation |
|------|---------|-------------|
| **Git for Windows** | Clone repository | https://git-scm.com/download/win |
| **Windows Terminal** | Better terminal | Microsoft Store or `winget install Microsoft.WindowsTerminal` |
| **VSCode** | Edit files remotely | https://code.visualstudio.com/ |
| **VSCode Remote-SSH** | SSH into droplet | VSCode Extensions |

## 📚 Detailed Guides

### For Beginners
- **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** - Step-by-step with screenshots
  - 10 simple steps
  - Copy-paste commands
  - No Linux knowledge required

### For Intermediate Users
- **[DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md)** - Complete Windows guide
  - All deployment methods
  - Troubleshooting section
  - Management commands
  - Monitoring setup

### For Advanced Users
- **[DEPLOYMENT_DIGITALOCEAN.md](DEPLOYMENT_DIGITALOCEAN.md)** - Full Docker guide
  - Docker architecture
  - Manual deployment
  - Performance tuning
  - Production best practices

## 🛠️ Available Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `deploy-to-do.ps1` | PowerShell | Automated deployment for Windows |
| `deploy-windows.bat` | cmd.exe | Batch script for Command Prompt |
| `deploy-to-do.sh` | Bash/WSL | Linux deployment script |
| `update-deployment.sh` | Droplet | Update running deployment |

## 📖 Documentation

| Document | Description |
|----------|-------------|
| `README_WINDOWS.md` | This file - Windows overview |
| `QUICKSTART_WINDOWS.md` | 5-minute quick start guide |
| `DEPLOYMENT_WINDOWS.md` | Complete Windows deployment guide |
| `DEPLOYMENT_DIGITALOCEAN.md` | Full Docker/Linux deployment guide |
| `README.md` | Main project README |
| `ARCHITECTURE.md` | System architecture |

## 🎯 Choose Your Path

### I'm New to This
→ Start with [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)

### I Want PowerShell
→ Use `deploy-to-do.ps1` + [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md)

### I Want Command Prompt
→ Use `deploy-windows.bat` + [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md)

### I Know Linux
→ Use WSL + [DEPLOYMENT_DIGITALOCEAN.md](DEPLOYMENT_DIGITALOCEAN.md)

### I Want Full Control
→ Manual steps in [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md)

## 💻 Common Windows Commands

### SSH Connection
```powershell
# Basic connection
ssh root@YOUR_DROPLET_IP

# With specific key
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@YOUR_DROPLET_IP
```

### Service Management
```powershell
# Start services
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose up -d"

# Stop services
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose down"

# Restart
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose restart"

# View logs
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose logs -f webhook"

# Status
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose ps"
```

### Testing
```powershell
# Health check
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/health"

# Test authentication
$body = @{device_id="pi_test";device_secret="test"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/device/auth" `
    -Method POST -ContentType "application/json" -Body $body
```

## 🔧 Troubleshooting

### SSH Issues

**"Permission denied (publickey)"**
```powershell
# Use password auth
ssh -o PreferredAuthentications=password root@YOUR_IP

# Or specify key
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@YOUR_IP
```

**"Connection refused"**
```powershell
# Check if droplet is running in Digital Ocean console
# Verify firewall allows SSH (port 22)

# Test with verbose
ssh -v root@YOUR_IP
```

**"Host key verification failed"**
```powershell
# Remove old host key
ssh-keygen -R YOUR_DROPLET_IP
```

### PowerShell Issues

**"Script cannot be loaded"**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Command not found"**
```powershell
# Ensure OpenSSH is installed
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Client*'

# If not installed
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### Service Issues

**Service won't start**
```bash
# SSH to droplet
ssh root@YOUR_IP

# Check logs
cd /opt/secure_voice
docker-compose logs webhook

# Check .env file
cat .env

# Restart
docker-compose down
docker-compose up -d
```

**Can't access webhook**
```powershell
# Check if firewall allows 80/443
ssh root@YOUR_IP "ufw status"

# Check nginx
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose logs nginx"

# Test locally on droplet
ssh root@YOUR_IP "curl http://localhost:8001/health"
```

### More Troubleshooting
See [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md) - Troubleshooting section

## 🖥️ Recommended Windows Setup

### Install Windows Terminal
```powershell
winget install Microsoft.WindowsTerminal
```

### Install Git for Windows
```powershell
winget install Git.Git
```

### Install VSCode
```powershell
winget install Microsoft.VisualStudioCode
```

### Configure SSH Config
```powershell
# Create SSH config file
notepad $env:USERPROFILE\.ssh\config
```

Add:
```
Host do-webhook
    HostName YOUR_DROPLET_IP
    User root
    IdentityFile ~/.ssh/id_ed25519
```

Now connect with:
```powershell
ssh do-webhook
```

## 📞 Support

- **Issues**: https://github.com/karthi1975/secure_voice/issues
- **Documentation**: See files in this repository
- **VAPI Docs**: https://docs.vapi.ai
- **Digital Ocean Docs**: https://docs.digitalocean.com

## 🎓 Learning Resources

### New to SSH?
- [Windows OpenSSH Guide](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)

### New to PowerShell?
- [PowerShell 101](https://docs.microsoft.com/en-us/powershell/scripting/learn/ps101/)

### New to Docker?
- [Docker Getting Started](https://docs.docker.com/get-started/)

### New to Digital Ocean?
- [Digital Ocean Tutorials](https://www.digitalocean.com/community/tutorials)

## 🔐 Security Notes

- ✅ Never commit `.env` file
- ✅ Use strong JWT_SECRET (32+ characters)
- ✅ Keep Windows and OpenSSH updated
- ✅ Use SSH keys, not passwords
- ✅ Enable Windows Defender Firewall
- ✅ Regular backups of `.env` and configs

## 💰 Costs

| Item | Cost |
|------|------|
| Digital Ocean Droplet | $12/month |
| Domain (optional) | ~$10/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total** | **~$12/month** |

## ✅ What You Get

After deployment:

- 🔒 Secure JWT authentication
- 🌐 HTTPS with auto-renewing SSL
- 🏠 Multi-tenant support
- ♾️ 24/7 uptime
- 📊 Built-in health monitoring
- 🔄 Auto-restart on failure
- 📝 Comprehensive logging
- 🛡️ Firewall configured

## 🚢 Architecture

```
Windows PC
    ↓ (SSH)
Digital Ocean Droplet (Ubuntu 22.04)
    ↓ (Docker)
┌─────────────────────────────────┐
│  Docker Containers              │
│  ├─ Nginx (80/443)             │
│  ├─ Webhook (8001)             │
│  └─ Certbot (SSL)              │
└─────────────────────────────────┘
    ↓
VAPI AI Platform
    ↓
Home Assistant
    ↓
Smart Devices
```

## 📝 License

MIT - Free to use and modify

## 🙏 Credits

- **VAPI**: https://vapi.ai
- **Digital Ocean**: https://digitalocean.com
- **Home Assistant**: https://home-assistant.io
- **Docker**: https://docker.com

---

**Need help?** Open an issue: https://github.com/karthi1975/secure_voice/issues
