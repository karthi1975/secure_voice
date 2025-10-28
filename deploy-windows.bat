@echo off
REM Deploy VAPI Webhook to Digital Ocean from Windows
REM Batch script for Windows Command Prompt

setlocal enabledelayedexpansion

REM Check for parameters
if "%1"=="" (
    echo Error: Droplet IP required
    echo.
    echo Usage: deploy-windows.bat DROPLET_IP [DOMAIN]
    echo.
    echo Examples:
    echo   deploy-windows.bat 192.168.1.100
    echo   deploy-windows.bat 192.168.1.100 webhook.example.com
    echo.
    exit /b 1
)

set DROPLET_IP=%1
set DOMAIN=%2
if "%DOMAIN%"=="" set DOMAIN=localhost

set APP_DIR=/opt/secure_voice
set REPO_URL=https://github.com/karthi1975/secure_voice.git
set SSH_USER=root

echo ========================================
echo Deploy to Digital Ocean - Windows
echo ========================================
echo.
echo Droplet IP: %DROPLET_IP%
echo Domain: %DOMAIN%
echo.

REM Check if SSH is available
where ssh >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] SSH client not found
    echo Please install OpenSSH client:
    echo   Settings -^> Apps -^> Optional Features -^> Add OpenSSH Client
    exit /b 1
)

echo [OK] SSH client found
echo.

REM Test SSH connection
echo Testing SSH connection to droplet...
ssh -o ConnectTimeout=5 -o BatchMode=yes %SSH_USER%@%DROPLET_IP% "echo connected" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Cannot connect to droplet with SSH key
    echo Make sure you have:
    echo   1. Added your SSH public key to Digital Ocean
    echo   2. SSH key is loaded in ssh-agent
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "!continue!"=="y" exit /b 1
) else (
    echo [OK] SSH connection successful
)

echo.
echo Creating deployment script on droplet...

REM Create temporary deployment script
set TEMP_SCRIPT=%TEMP%\deploy-do.sh

(
echo #!/bin/bash
echo set -e
echo.
echo # Colors
echo RED='\033[0;31m'
echo GREEN='\033[0;32m'
echo YELLOW='\033[1;33m'
echo NC='\033[0m'
echo.
echo echo -e "${YELLOW}Starting deployment....${NC}"
echo.
echo # Update system
echo echo -e "${YELLOW}Updating system packages...${NC}"
echo export DEBIAN_FRONTEND=noninteractive
echo apt-get update
echo apt-get upgrade -y
echo.
echo # Install Docker
echo if ! command -v docker ^&^> /dev/null; then
echo     echo -e "${YELLOW}Installing Docker...${NC}"
echo     curl -fsSL https://get.docker.com -o get-docker.sh
echo     sh get-docker.sh
echo     rm get-docker.sh
echo     systemctl enable docker
echo     systemctl start docker
echo     echo -e "${GREEN}Docker installed${NC}"
echo else
echo     echo -e "${GREEN}Docker already installed${NC}"
echo fi
echo.
echo # Install Docker Compose
echo if ! command -v docker-compose ^&^> /dev/null; then
echo     echo -e "${YELLOW}Installing Docker Compose...${NC}"
echo     curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s^)-$(uname -m^)" -o /usr/local/bin/docker-compose
echo     chmod +x /usr/local/bin/docker-compose
echo     echo -e "${GREEN}Docker Compose installed${NC}"
echo else
echo     echo -e "${GREEN}Docker Compose already installed${NC}"
echo fi
echo.
echo # Create app directory
echo mkdir -p %APP_DIR%
echo cd %APP_DIR%
echo.
echo # Clone or update repository
echo if [ -d ".git" ]; then
echo     echo -e "${YELLOW}Updating repository...${NC}"
echo     git pull
echo else
echo     echo -e "${YELLOW}Cloning repository...${NC}"
echo     git clone %REPO_URL% .
echo fi
echo.
echo # Create .env file
echo if [ ! -f ".env" ]; then
echo     echo -e "${YELLOW}Creating .env file...${NC}"
echo     cp .env.example .env
echo     echo -e "${RED}IMPORTANT: Edit .env file with your credentials!${NC}"
echo fi
echo.
echo # Update nginx domain
echo if [ "%DOMAIN%" != "localhost" ]; then
echo     echo -e "${YELLOW}Updating nginx configuration...${NC}"
echo     sed -i "s/your-domain.com/%DOMAIN%/g" nginx/conf.d/webhook.conf
echo fi
echo.
echo # Create certbot directories
echo mkdir -p certbot/conf certbot/www
echo.
echo # Configure firewall
echo if command -v ufw ^&^> /dev/null; then
echo     echo -e "${YELLOW}Configuring firewall...${NC}"
echo     ufw --force enable
echo     ufw allow OpenSSH
echo     ufw allow 80/tcp
echo     ufw allow 443/tcp
echo     echo -e "${GREEN}Firewall configured${NC}"
echo fi
echo.
echo echo -e "${GREEN}Deployment preparation complete!${NC}"
echo echo -e "${YELLOW}Next steps:${NC}"
echo echo -e "  1. Edit .env file: nano %APP_DIR%/.env"
echo echo -e "  2. Start services: cd %APP_DIR% ^&^& docker-compose up -d"
) > "%TEMP_SCRIPT%"

echo.
echo Uploading deployment script...

REM Upload script
type "%TEMP_SCRIPT%" | ssh %SSH_USER%@%DROPLET_IP% "cat > /tmp/deploy.sh"
if %ERRORLEVEL% neq 0 (
    echo Failed to upload deployment script
    exit /b 1
)

ssh %SSH_USER%@%DROPLET_IP% "chmod +x /tmp/deploy.sh"

echo.
echo Running deployment script on droplet...
echo This may take 5-10 minutes...
echo.

REM Run deployment
ssh %SSH_USER%@%DROPLET_IP% "bash /tmp/deploy.sh"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo Deployment Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo.
    echo 1. Connect to your droplet:
    echo    ssh root@%DROPLET_IP%
    echo.
    echo 2. Edit the .env file:
    echo    nano %APP_DIR%/.env
    echo.
    echo    Update these variables:
    echo    - VAPI_API_KEY=your_actual_key
    echo    - JWT_SECRET=$(openssl rand -base64 32^)
    echo    - DOMAIN=%DOMAIN%
    echo.
    echo 3. Start the services:
    echo    cd %APP_DIR%
    echo    docker-compose up -d
    echo.
    echo 4. Check service status:
    echo    docker-compose ps
    echo    docker-compose logs -f webhook
    echo.

    if not "%DOMAIN%"=="localhost" (
        echo 5. Access your webhook at:
        echo    https://%DOMAIN%
        echo.
        echo 6. Update VAPI webhook URL to:
        echo    https://%DOMAIN%/webhook?device_id={{device_id}}
    ) else (
        echo 5. Access your webhook at:
        echo    http://%DROPLET_IP%:8001
    )
    echo.
) else (
    echo.
    echo Deployment failed! Check the error messages above.
    exit /b 1
)

REM Cleanup
del "%TEMP_SCRIPT%" >nul 2>&1

endlocal
