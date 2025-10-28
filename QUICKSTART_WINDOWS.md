# Quick Start Guide for Windows Users

Deploy VAPI Webhook to Digital Ocean from Windows in 5 minutes.

## Prerequisites

✅ Windows 10/11
✅ PowerShell (built-in)
✅ OpenSSH Client
✅ Digital Ocean account

## Step 1: Install OpenSSH (if needed)

Check if you have SSH:
```powershell
ssh -V
```

If not found, install it:
```
Settings → Apps → Optional Features → Add a feature → OpenSSH Client → Install
```

## Step 2: Generate SSH Key

```powershell
# Open PowerShell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter 3 times (accept defaults, no passphrase)
```

View your public key:
```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

## Step 3: Add SSH Key to Digital Ocean

1. Copy the public key output from Step 2
2. Go to https://cloud.digitalocean.com/account/security
3. Click **"Add SSH Key"**
4. Paste your key and name it (e.g., "Windows Laptop")
5. Click **"Add SSH Key"**

## Step 4: Create Droplet

1. Go to https://cloud.digitalocean.com/droplets
2. Click **"Create Droplet"**
3. Choose:
   - Image: **Ubuntu 22.04 LTS**
   - Plan: **Basic $12/mo** (2GB RAM)
   - Region: Closest to you
   - Authentication: **SSH keys** (select your key)
4. Click **"Create Droplet"**
5. **Copy the IP address** shown

## Step 5: Deploy with PowerShell

Download this repository:
```powershell
cd $env:USERPROFILE\Downloads
git clone https://github.com/karthi1975/secure_voice.git
cd secure_voice
```

Run deployment (replace `YOUR_IP` with droplet IP):
```powershell
# Without domain (HTTP only)
.\deploy-to-do.ps1 -DropletIP YOUR_IP

# With domain (for HTTPS)
.\deploy-to-do.ps1 -DropletIP YOUR_IP -Domain webhook.yourdomain.com
```

Example:
```powershell
.\deploy-to-do.ps1 -DropletIP 157.245.123.45 -Domain webhook.example.com
```

Wait 5-10 minutes for installation...

## Step 6: Configure Environment

When deployment completes, SSH into droplet:
```powershell
ssh root@YOUR_IP
```

Edit configuration file:
```bash
nano /opt/secure_voice/.env
```

Update these lines:
```bash
VAPI_API_KEY=your_actual_vapi_api_key_here
JWT_SECRET=use_command_openssl_rand_base64_32_to_generate
DOMAIN=webhook.yourdomain.com
```

Save: Press `Ctrl+X`, then `Y`, then `Enter`

## Step 7: Start Services

```bash
cd /opt/secure_voice
docker-compose up -d
```

Check status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f webhook
```

Press `Ctrl+C` to exit logs

## Step 8: Test Deployment

```bash
# Test health endpoint
curl http://localhost:8001/health
# Should show: {"status":"healthy"}
```

Exit SSH:
```bash
exit
```

## Step 9: Update VAPI

1. Go to https://dashboard.vapi.ai/
2. Select your assistant
3. Update **Server URL** to:
   ```
   https://webhook.yourdomain.com/webhook?device_id={{device_id}}
   ```
   Or if no domain:
   ```
   http://YOUR_DROPLET_IP:8001/webhook?device_id={{device_id}}
   ```

## Step 10: Test from Windows

```powershell
# Test health (replace with your domain or IP)
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/health"

# Should return: @{status=healthy}
```

## ✅ You're Done!

Your webhook is now deployed and running on Digital Ocean!

## Common Tasks

### View Logs
```powershell
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose logs -f webhook"
```

### Restart Service
```powershell
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose restart"
```

### Update Code
```powershell
ssh root@YOUR_IP "cd /opt/secure_voice && git pull && docker-compose up -d --build"
```

### Stop Service
```powershell
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose down"
```

## Troubleshooting

### Can't SSH to Droplet
```powershell
# Make sure SSH key is added to Digital Ocean
# Try with password instead
ssh root@YOUR_IP
```

### "Permission denied (publickey)"
```powershell
# Specify your key file explicitly
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@YOUR_IP
```

### PowerShell Script Won't Run
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Service Not Starting
```bash
# SSH to droplet and check logs
ssh root@YOUR_IP
cd /opt/secure_voice
docker-compose logs webhook
```

## Need More Help?

- **Full Windows Guide**: See `DEPLOYMENT_WINDOWS.md`
- **Full Docker Guide**: See `DEPLOYMENT_DIGITALOCEAN.md`
- **Architecture**: See `ARCHITECTURE.md`
- **GitHub Issues**: https://github.com/karthi1975/secure_voice/issues

## Windows Tools (Optional but Recommended)

### Windows Terminal
Better terminal experience:
```powershell
winget install Microsoft.WindowsTerminal
```

### VSCode with Remote SSH
Edit files on droplet directly from Windows:
1. Install VSCode: https://code.visualstudio.com/
2. Install "Remote - SSH" extension
3. Press `F1` → "Remote-SSH: Connect to Host"
4. Enter `root@YOUR_IP`
5. Open folder: `/opt/secure_voice`

### WinSCP
GUI for file transfers:
1. Download: https://winscp.net/
2. Connect to droplet
3. Drag and drop files

## Quick Commands Reference

```powershell
# Connect to droplet
ssh root@YOUR_IP

# View service status
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose ps"

# View logs
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose logs -f"

# Restart
ssh root@YOUR_IP "cd /opt/secure_voice && docker-compose restart"

# Update
ssh root@YOUR_IP "cd /opt/secure_voice && git pull && docker-compose up -d --build"

# Test health
Invoke-RestMethod -Uri "https://webhook.yourdomain.com/health"
```

## What's Deployed?

- **FastAPI Webhook Service** (Port 8001)
- **Nginx Reverse Proxy** (Ports 80/443)
- **Certbot** (Auto SSL renewal)
- **Docker Containers** (Isolated, secure)

Your webhook handles:
- ✅ Device authentication (JWT tokens)
- ✅ VAPI webhook events
- ✅ Multi-tenant routing
- ✅ Home Assistant integration

## Next Steps

1. **Configure Multi-Tenant** (optional):
   - Edit `webhook_service/device_auth.py`
   - Edit `webhook_service/ha_instances.py`
   - Restart: `docker-compose restart`

2. **Setup Monitoring** (optional):
   - Use PowerShell monitoring script
   - Or UptimeRobot: https://uptimerobot.com/

3. **Deploy Raspberry Pi Client**:
   - See `README.md` for Pi setup
   - Configure with device_id and device_secret

## Cost

- **Droplet**: $12/month (2GB RAM)
- **Domain**: ~$10/year (optional)
- **SSL Certificate**: Free (Let's Encrypt)

**Total**: ~$12/month

## Security

✅ JWT tokens (15 min expiry)
✅ HTTPS with SSL
✅ Firewall configured
✅ Non-root containers
✅ VAPI API key never on edge devices

## License

MIT - Free to use and modify
